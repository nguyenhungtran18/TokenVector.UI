// Harness tam: decode gop.264 qua shim, in dims + rgb sum.
using System;
using System.IO;

public static class ShimTest
{
    public static int Main(string[] args)
    {
        string dir = args.Length > 0 ? args[0] : "build/ingest";
        byte[] bs = File.ReadAllBytes(Path.Combine(dir, "gop.264"));
        int id = OpenH264Shim.Create();
        Console.WriteLine("create id=" + id);
        if (id <= 0) return 1;
        int rc = OpenH264Shim.Init(id);
        Console.WriteLine("init rc=" + rc);
        if (rc != 0) return 1;
        // nap NALs (Annex B): tach theo start code, feed tung NAL
        int frames = 0;
        int i = 0;
        byte[] rgb = null;
        int w = 0, h = 0;
        while (i < bs.Length)
        {
            int j = i + 4;
            while (j + 4 < bs.Length && !(bs[j] == 0 && bs[j + 1] == 0 && bs[j + 2] == 0 && bs[j + 3] == 1)) j++;
            int start = i, end = (j + 4 <= bs.Length) ? j : bs.Length;
            unsafe
            {
                fixed (byte* p = &bs[start])
                {
                    int st = OpenH264Shim.Decode(id, (long)p, end - start);
                    if (st != 0) Console.WriteLine("nal rc=" + st);
                    if (OpenH264Shim.HasFrame(id) == 1)
                    {
                        w = OpenH264Shim.FrameW(id);
                        h = OpenH264Shim.FrameH(id);
                        if (frames == 0) Console.WriteLine("YUV0=" + OpenH264Shim.DbgYuv(id));
                        rgb = new byte[w * h * 3];
                        fixed (byte* q = rgb)
                        {
                            int n = OpenH264Shim.CopyFrameRgb(id, (long)q);
                            long sum = 0;
                            foreach (byte b in rgb) sum += b;
                            Console.WriteLine("frame " + frames + " " + w + "x" + h + " bytes=" + n + " sum=" + sum);
                            if (frames == 0)
                            {
                                OpenH264Shim.DumpPlanes(id, Path.Combine(dir, "pyuv.bin"));
                                Console.WriteLine("saved pyuv.bin");
                                var bmp = new System.Drawing.Bitmap(w, h, System.Drawing.Imaging.PixelFormat.Format24bppRgb);
                                var bd = bmp.LockBits(new System.Drawing.Rectangle(0, 0, w, h), System.Drawing.Imaging.ImageLockMode.WriteOnly, bmp.PixelFormat);
                                int stride = bd.Stride;
                                byte[] flat = new byte[stride * h];
                                for (int yy = 0; yy < h; yy++)
                                    Array.Copy(rgb, yy * w * 3, flat, yy * stride, w * 3);
                                System.Runtime.InteropServices.Marshal.Copy(flat, 0, bd.Scan0, flat.Length);
                                bmp.UnlockBits(bd);
                                bmp.Save(Path.Combine(dir, "dec0.png"));
                                Console.WriteLine("saved dec0.png");
                            }
                            frames++;
                        }
                    }
                }
            }
            i = end;
            if (frames >= 6) break;
        }
        // flush
        OpenH264Shim.Flush(id);
        if (OpenH264Shim.HasFrame(id) == 1)
        {
            w = OpenH264Shim.FrameW(id);
            h = OpenH264Shim.FrameH(id);
            rgb = new byte[w * h * 3];
            unsafe
            {
                fixed (byte* q = rgb)
                {
                    int n = OpenH264Shim.CopyFrameRgb(id, (long)q);
                    long sum = 0;
                    foreach (byte b in rgb) sum += b;
                    Console.WriteLine("frame " + frames + " " + w + "x" + h + " bytes=" + n + " sum=" + sum + " (flush)");
                    frames++;
                }
            }
        }
        OpenH264Shim.Destroy(id);
        Console.WriteLine("FRAMES=" + frames);
        return frames > 0 ? 0 : 1;
    }
}
