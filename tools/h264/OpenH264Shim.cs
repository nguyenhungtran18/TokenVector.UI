// OpenH264Shim - bridge mong C# cho TkvUI.H264 (.tkv chi trao kieu co ban).
// Ly do shim: SDecodingParam/SBufferInfo can struct marshal ma tkvc chua co;
// shim giu struct trong C#, .tkv chi goi qua (int/long) + R2 buffers.
// Build: csc /target:library /out:build/OpenH264Shim.dll tools/h264/OpenH264Shim.cs
// (tools/verify.sh tu build khi thieu + copy ra OUT/). MIT - cung license repo.
using System;
using System.Collections.Generic;
using System.IO;
using System.Reflection;
using System.Runtime.InteropServices;

public static class OpenH264Shim
{
    const string DLL = "openh264-win64.dll";

    [DllImport("kernel32.dll", CharSet = CharSet.Auto)]
    static extern bool SetDllDirectory(string path);

    [DllImport(DLL, EntryPoint = "WelsCreateDecoder")]
    static extern int NativeCreate(out IntPtr ppDecoder);
    [DllImport(DLL, EntryPoint = "WelsDestroyDecoder")]
    static extern void NativeDestroy(IntPtr pDecoder);
    [DllImport("kernel32.dll", EntryPoint = "RtlMoveMemory")]
    static extern void CopyMem(IntPtr dst, IntPtr src, int len);

    [UnmanagedFunctionPointer(CallingConvention.StdCall)]
    delegate int InitFn(IntPtr self, ref SDecodingParam p);
    [UnmanagedFunctionPointer(CallingConvention.StdCall)]
    delegate int Decode2Fn(IntPtr self, IntPtr src, int len, IntPtr ppDst, IntPtr pInfo);
    [UnmanagedFunctionPointer(CallingConvention.StdCall)]
    delegate int FlushFn(IntPtr self, IntPtr ppDst, IntPtr pInfo);

    [StructLayout(LayoutKind.Sequential)]
    struct SDecodingParam
    {
        public IntPtr pFileNameRestructed;
        public uint uiCpuLoad;
        public byte uiTargetDqLayer;
        public int eEcActiveIdc;
        [MarshalAs(UnmanagedType.I1)] public bool bParseOnly;
        public uint sVideoPropertySize;
    }

    class DecoderState
    {
        public IntPtr dec;
        public IntPtr info;
        public IntPtr dst;
        public InitFn initFn;
        public Decode2Fn decFn;
        public FlushFn flushFn;
    }

    static Dictionary<int, DecoderState> states = new Dictionary<int, DecoderState>();
    static int nextId = 1;

    static OpenH264Shim()
    {
        try
        {
            string exe = Path.GetDirectoryName(Assembly.GetExecutingAssembly().Location);
            string cwd = Directory.GetCurrentDirectory();
            string[] dirs = { exe, Path.Combine(exe, ".."), cwd, Path.Combine(cwd, "build") };
            foreach (string d in dirs)
            {
                try
                {
                    if (d != null && File.Exists(Path.Combine(d, DLL)))
                    {
                        SetDllDirectory(Path.GetFullPath(d));
                        break;
                    }
                }
                catch { }
            }
        }
        catch { }
    }

    static T Vfn<T>(IntPtr obj, int slot)
    {
        IntPtr vt = Marshal.ReadIntPtr(obj);
        IntPtr fn = Marshal.ReadIntPtr(vt, slot * IntPtr.Size);
        return (T)(object)Marshal.GetDelegateForFunctionPointer(fn, typeof(T));
    }

    static void Zero(IntPtr p, int n)
    {
        for (int i = 0; i < n; i++) Marshal.WriteByte(p, i, 0);
    }

    public static int Create()
    {
        try
        {
            IntPtr dec;
            if (NativeCreate(out dec) != 0 || dec == IntPtr.Zero) return 0;
            DecoderState st = new DecoderState();
            st.dec = dec;
            st.info = Marshal.AllocHGlobal(72);
            st.dst = Marshal.AllocHGlobal(24);
            Zero(st.info, 72);
            Zero(st.dst, 24);
            st.initFn = Vfn<InitFn>(dec, 0);
            st.decFn = Vfn<Decode2Fn>(dec, 4);
            st.flushFn = Vfn<FlushFn>(dec, 5);
            int id = nextId++;
            states[id] = st;
            return id;
        }
        catch { return 0; }
    }

    public static int Init(int id)
    {
        DecoderState st;
        if (!states.TryGetValue(id, out st)) return -1;
        try
        {
            SDecodingParam par = new SDecodingParam();
            par.pFileNameRestructed = IntPtr.Zero;
            par.uiCpuLoad = 0;
            par.uiTargetDqLayer = 255;
            par.eEcActiveIdc = 0;
            par.bParseOnly = false;
            par.sVideoPropertySize = 0;
            return st.initFn(st.dec, ref par);
        }
        catch { return -1; }
    }

    public static int Decode(int id, long srcPtr, int len)
    {
        DecoderState st;
        if (!states.TryGetValue(id, out st)) return -1;
        try
        {
            Zero(st.info, 72);
            return st.decFn(st.dec, (IntPtr)srcPtr, len, st.dst, st.info);
        }
        catch { return -1; }
    }

    public static int Flush(int id)
    {
        DecoderState st;
        if (!states.TryGetValue(id, out st)) return -1;
        try
        {
            Zero(st.info, 72);
            return st.flushFn(st.dec, st.dst, st.info);
        }
        catch { return -1; }
    }

    public static int HasFrame(int id)
    {
        DecoderState st;
        if (!states.TryGetValue(id, out st)) return 0;
        return Marshal.ReadInt32(st.info, 0);
    }

    public static int FrameW(int id)
    {
        DecoderState st;
        if (!states.TryGetValue(id, out st)) return 0;
        return Marshal.ReadInt32(st.info, 24);
    }

    public static int FrameH(int id)
    {
        DecoderState st;
        if (!states.TryGetValue(id, out st)) return 0;
        return Marshal.ReadInt32(st.info, 28);
    }

    static int Clip(int v) { return v < 0 ? 0 : (v > 255 ? 255 : v); }

    public static string DbgYuv(int id)
    {
        DecoderState st;
        if (!states.TryGetValue(id, out st)) return "no";
        int w = Marshal.ReadInt32(st.info, 24);
        int h = Marshal.ReadInt32(st.info, 28);
        int s0 = Marshal.ReadInt32(st.info, 36);
        int s1 = Marshal.ReadInt32(st.info, 40);
        IntPtr py = Marshal.ReadIntPtr(st.dst, 0);
        IntPtr pu = Marshal.ReadIntPtr(st.dst, 8);
        IntPtr pv = Marshal.ReadIntPtr(st.dst, 16);
        string r = "wh=" + w + "x" + h + " s0=" + s0 + " s1=" + s1;
        r += " Y=" + Marshal.ReadByte(py, 100000) + "," + Marshal.ReadByte(py, 100001) + "," + Marshal.ReadByte(py, 100002);
        r += " U=" + Marshal.ReadByte(pu, 50000) + "," + Marshal.ReadByte(pu, 50001);
        r += " V=" + Marshal.ReadByte(pv, 50000) + "," + Marshal.ReadByte(pv, 50001);
        return r;
    }

    public static int DumpPlanes(int id, string path)
    {
        DecoderState st;
        if (!states.TryGetValue(id, out st)) return 0;
        int w = Marshal.ReadInt32(st.info, 24);
        int h = Marshal.ReadInt32(st.info, 28);
        int s0 = Marshal.ReadInt32(st.info, 36);
        int s1 = Marshal.ReadInt32(st.info, 40);
        IntPtr py = Marshal.ReadIntPtr(st.dst, 0);
        IntPtr pu = Marshal.ReadIntPtr(st.dst, 8);
        IntPtr pv = Marshal.ReadIntPtr(st.dst, 16);
        byte[] yb = new byte[h * s0];
        byte[] ub = new byte[(h >> 1) * s1];
        byte[] vb = new byte[(h >> 1) * s1];
        Marshal.Copy(py, yb, 0, yb.Length);
        Marshal.Copy(pu, ub, 0, ub.Length);
        Marshal.Copy(pv, vb, 0, vb.Length);
        using (FileStream fs = new FileStream(path, FileMode.Create))
        {
            byte[] hdr = System.Text.Encoding.ASCII.GetBytes(w + " " + h + " " + s0 + " " + s1 + "\n");
            fs.Write(hdr, 0, hdr.Length);
            fs.Write(yb, 0, yb.Length);
            fs.Write(ub, 0, ub.Length);
            fs.Write(vb, 0, vb.Length);
        }
        return yb.Length + ub.Length + vb.Length;
    }

    public static int CopyFrameRgb(int id, long dstPtr)
    {
        DecoderState st;
        if (!states.TryGetValue(id, out st)) return 0;
        int w = Marshal.ReadInt32(st.info, 24);
        int h = Marshal.ReadInt32(st.info, 28);
        int s0 = Marshal.ReadInt32(st.info, 36);
        int s1 = Marshal.ReadInt32(st.info, 40);
        if (w <= 0 || h <= 0 || w > 4096 || h > 4096) return 0;
        IntPtr py = Marshal.ReadIntPtr(st.dst, 0);
        IntPtr pu = Marshal.ReadIntPtr(st.dst, 8);
        IntPtr pv = Marshal.ReadIntPtr(st.dst, 16);
        if (py == IntPtr.Zero || pu == IntPtr.Zero || pv == IntPtr.Zero) return 0;
        int h2 = h >> 1;
        byte[] yb = new byte[h * s0];
        byte[] ub = new byte[h2 * s1];
        byte[] vb = new byte[h2 * s1];
        Marshal.Copy(py, yb, 0, yb.Length);
        Marshal.Copy(pu, ub, 0, ub.Length);
        Marshal.Copy(pv, vb, 0, vb.Length);
        byte[] rgb = new byte[w * h * 3];
        int o = 0;
        for (int y = 0; y < h; y++)
        {
            int yo = y * s0;
            int uvo = (y >> 1) * s1;
            for (int x = 0; x < w; x++)
            {
                int Y = yb[yo + x];
                int U = ub[uvo + (x >> 1)];
                int V = vb[uvo + (x >> 1)];
                int C = Y - 16, D = U - 128, E = V - 128;
                rgb[o] = (byte)Clip((298 * C + 459 * E + 128) >> 8);
                rgb[o + 1] = (byte)Clip((298 * C - 55 * D - 136 * E + 128) >> 8);
                rgb[o + 2] = (byte)Clip((298 * C + 541 * D + 128) >> 8);
                o += 3;
            }
        }
        Marshal.Copy(rgb, 0, (IntPtr)dstPtr, rgb.Length);
        return rgb.Length;
    }

    public static void Destroy(int id)
    {
        DecoderState st;
        if (!states.TryGetValue(id, out st)) return;
        try
        {
            NativeDestroy(st.dec);
            Marshal.FreeHGlobal(st.info);
            Marshal.FreeHGlobal(st.dst);
        }
        catch { }
        states.Remove(id);
    }
}
