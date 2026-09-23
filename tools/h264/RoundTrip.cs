// Round-trip: OpenH264 encoder -> Annex B -> shim decoder -> RGB.
// Layout mode: "hdr" = default MSVC x64 (pData@24, w@56, h@60); "old" = legacy probe (pData@20, w@52, h@56).
using System;
using System.Collections.Generic;
using System.IO;
using System.Runtime.InteropServices;

public static class RoundTrip
{
    const string DLL = "openh264-win64.dll";
    [DllImport(DLL, EntryPoint = "WelsCreateSVCEncoder")]
    static extern int EncCreate(out IntPtr pp);
    [DllImport(DLL, EntryPoint = "WelsDestroySVCEncoder")]
    static extern void EncDestroy(IntPtr p);

    [UnmanagedFunctionPointer(CallingConvention.StdCall)]
    delegate int Fn2(IntPtr self, IntPtr a);
    [UnmanagedFunctionPointer(CallingConvention.StdCall)]
    delegate int Fn3(IntPtr self, IntPtr a, IntPtr b);

    static T Vfn<T>(IntPtr obj, int slot)
    {
        IntPtr vt = Marshal.ReadIntPtr(obj);
        return (T)(object)Marshal.GetDelegateForFunctionPointer(Marshal.ReadIntPtr(vt, slot * IntPtr.Size), typeof(T));
    }
    static void Zero(IntPtr p, int n) { for (int i = 0; i < n; i++) Marshal.WriteByte(p, i, 0); }

    static string Head(byte[] b, int max)
    {
        string s = "";
        for (int i = 0; i < b.Length && i < max; i++) s += b[i].ToString("X2") + " ";
        return s;
    }

    // SFrameBSInfo: iLayerNum@0, sLayerInfo@8 (SLayerBSInfo=56B):
    // iNalCount@16, pNalLen@24, pBsBuf@32 — concatenate ALL layers.
    static byte[] ExtractBs(IntPtr info, string tag)
    {
        int layers = Marshal.ReadInt32(info, 0);
        if (layers <= 0) { Console.WriteLine(tag + " layers=" + layers); return new byte[0]; }
        var acc = new List<byte>();
        int nalsTotal = 0;
        for (int L = 0; L < layers; L++)
        {
            int b = 8 + L * 56;
            int nals = Marshal.ReadInt32(info, b + 16);
            IntPtr pLen = Marshal.ReadIntPtr(info, b + 24);
            IntPtr pBs = Marshal.ReadIntPtr(info, b + 32);
            if (nals <= 0 || pLen == IntPtr.Zero || pBs == IntPtr.Zero) continue;
            int total = 0;
            for (int k = 0; k < nals; k++) total += Marshal.ReadInt32(pLen, k * 4);
            if (total <= 0 || total > 1 << 20) continue;
            byte[] part = new byte[total];
            Marshal.Copy(pBs, part, 0, total);
            acc.AddRange(part);
            nalsTotal += nals;
        }
        byte[] bs = acc.ToArray();
        Console.WriteLine(tag + " layers=" + layers + " nals=" + nalsTotal + " bytes=" + bs.Length + " head=" + Head(bs, 32));
        return bs;
    }

    static byte[] Solid(int w, int h, byte y)
    {
        byte[] r = new byte[w * h * 3 / 2];
        for (int i = 0; i < w * h; i++) r[i] = y;
        for (int i = w * h; i < r.Length; i++) r[i] = 128;
        return r;
    }

    public static int Main(string[] args)
    {
        string mode = args.Length > 0 ? args[0] : "hdr";
        int w = 64, h = 64;
        int pDataOff = mode == "old" ? 20 : 24;
        int wOff = mode == "old" ? 52 : 56;
        int hOff = mode == "old" ? 56 : 60;
        int tsOff = mode == "old" ? 60 : 64;
        Console.WriteLine("layout=" + mode + " pData@" + pDataOff + " w@" + wOff + " h@" + hOff);

        IntPtr enc;
        if (EncCreate(out enc) != 0 || enc == IntPtr.Zero) { Console.WriteLine("enc create FAIL"); return 1; }

        // SEncParamBase 24B: usage@0 w@4 h@8 bitrate@12 rc@16 fps@20
        IntPtr ep = Marshal.AllocHGlobal(24);
        Zero(ep, 24);
        Marshal.WriteInt32(ep, 4, w);
        Marshal.WriteInt32(ep, 8, h);
        Marshal.WriteInt32(ep, 12, 500000);
        Marshal.WriteInt32(ep, 16, 0);
        Marshal.Copy(BitConverter.GetBytes(30.0f), 0, (IntPtr)(ep.ToInt64() + 20), 4);
        Fn2 initE = Vfn<Fn2>(enc, 0);
        int erc = initE(enc, ep);
        Console.WriteLine("init rc=" + erc);
        if (erc != 0) { EncDestroy(enc); return 1; }

        IntPtr fmtb = Marshal.AllocHGlobal(4);
        Marshal.WriteInt32(fmtb, 0, 23);
        Fn3 setOpt = Vfn<Fn3>(enc, 7);
        int sorc = setOpt(enc, IntPtr.Zero, fmtb);
        Console.WriteLine("setopt DATAFORMAT rc=" + sorc);
        Marshal.FreeHGlobal(fmtb);

        IntPtr einf = Marshal.AllocHGlobal(16384);
        Zero(einf, 16384);
        Fn2 encParams = Vfn<Fn2>(enc, 5);
        int eprc = encParams(enc, einf);
        byte[] phead = ExtractBs(einf, "paramsets");
        Console.WriteLine("paramsets rc=" + eprc + " bytes=" + phead.Length);
        Marshal.FreeHGlobal(einf);

        Fn3 forceIdr = Vfn<Fn3>(enc, 6);
        int frc = forceIdr(enc, new IntPtr(1), new IntPtr(-1));
        Console.WriteLine("forceidr rc=" + frc);

        IntPtr pic = Marshal.AllocHGlobal(80);
        Zero(pic, 80);
        IntPtr info = Marshal.AllocHGlobal(16384);
        Marshal.WriteInt32(pic, 0, 23);
        Marshal.WriteInt32(pic, 4, w);
        Marshal.WriteInt32(pic, 8, w >> 1);
        Marshal.WriteInt32(pic, 12, w >> 1);
        Marshal.WriteInt32(pic, 16, 0);
        Marshal.WriteInt32(pic, wOff, w);
        Marshal.WriteInt32(pic, hOff, h);

        Fn3 encFrame = Vfn<Fn3>(enc, 4);
        var outs = new List<byte[]>();
        for (int ff = 0; ff < 12; ff++)
        {
            byte[] yuv = Solid(w, h, (byte)(30 + ff * 15));
            IntPtr yb = Marshal.AllocHGlobal(yuv.Length);
            Marshal.Copy(yuv, 0, yb, yuv.Length);
            Marshal.WriteIntPtr(pic, pDataOff, yb);
            Marshal.WriteIntPtr(pic, pDataOff + 8, (IntPtr)(yb.ToInt64() + w * h));
            Marshal.WriteIntPtr(pic, pDataOff + 16, (IntPtr)(yb.ToInt64() + w * h + (w * h >> 2)));
            Marshal.WriteIntPtr(pic, pDataOff + 24, IntPtr.Zero);
            Marshal.WriteInt64(pic, tsOff, ff * 33L);
            Zero(info, 16384);
            int rc = encFrame(enc, pic, info);
            byte[] bs = rc >= 0 ? ExtractBs(info, "enc" + ff) : new byte[0];
            if (bs.Length > 0) outs.Add(bs);
            else Console.WriteLine("enc" + ff + " rc=" + rc + " (no bs)");
            Marshal.FreeHGlobal(yb);
        }
        Console.WriteLine("encoded frames=" + outs.Count);

        // save Annex B for inspection / external tools
        string outPath = Path.Combine("build", "ingest", "enc_out.264");
        using (FileStream fs = new FileStream(outPath, FileMode.Create))
        {
            if (phead.Length > 0) fs.Write(phead, 0, phead.Length);
            foreach (byte[] b in outs) fs.Write(b, 0, b.Length);
        }
        Console.WriteLine("saved " + outPath + " total=" + (phead.Length + Sum(outs)));

        // decode via proven shim path: feed phead, then each frame buffer whole
        int id = OpenH264Shim.Create();
        int irc = OpenH264Shim.Init(id);
        Console.WriteLine("shim create id=" + id + " init rc=" + irc);
        if (id <= 0) return 1;
        int di = 0;
        unsafe
        {
            if (phead.Length > 0)
            {
                fixed (byte* p = phead)
                {
                    int st = OpenH264Shim.Decode(id, (long)p, phead.Length);
                    Console.WriteLine("feed phead rc=" + st);
                }
            }
            foreach (byte[] bs in outs)
            {
                fixed (byte* p = bs)
                {
                    int st = OpenH264Shim.Decode(id, (long)p, bs.Length);
                    int has = OpenH264Shim.HasFrame(id);
                    Console.WriteLine("feed frame rc=" + st + " has=" + has);
                    if (has == 1)
                    {
                        int dw = OpenH264Shim.FrameW(id), dh = OpenH264Shim.FrameH(id);
                        byte[] rgb = new byte[dw * dh * 3];
                        fixed (byte* q = rgb)
                        {
                            OpenH264Shim.CopyFrameRgb(id, (long)q);
                            long sr = 0, sg = 0, sb = 0;
                            for (int k = 0; k < rgb.Length; k += 3) { sr += rgb[k]; sg += rgb[k + 1]; sb += rgb[k + 2]; }
                            int n = rgb.Length / 3;
                            Console.WriteLine("dec " + di + " " + dw + "x" + dh + " avg=" + (sr / n) + "," + (sg / n) + "," + (sb / n));
                            di++;
                        }
                    }
                }
            }
        }
        OpenH264Shim.Flush(id);
        if (OpenH264Shim.HasFrame(id) == 1) di++;
        OpenH264Shim.Destroy(id);

        Marshal.FreeHGlobal(pic);
        Marshal.FreeHGlobal(info);
        Marshal.FreeHGlobal(ep);
        EncDestroy(enc);
        Console.WriteLine("RT_DONE decoded=" + di);
        return di >= 1 ? 0 : 1;
    }

    static int Sum(List<byte[]> xs)
    {
        int t = 0;
        foreach (byte[] b in xs) t += b.Length;
        return t;
    }
}
