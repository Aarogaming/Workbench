using System;
using System.Drawing;
using System.Threading;
using System.Windows.Forms;
using System.IO;
using System.Runtime.InteropServices;


using System;
using System.Drawing;
using System.Threading;
using System.Windows.Forms;
using System.IO;
using System.Runtime.InteropServices;

namespace VSCodeChatCapture
{
    [StructLayout(LayoutKind.Sequential)]
    public struct INPUT
    {
        public int type;
        public InputUnion U;
    }

    [StructLayout(LayoutKind.Explicit)]
    public struct InputUnion
    {
        [FieldOffset(0)]
        public MOUSEINPUT mi;
    }

    [StructLayout(LayoutKind.Sequential)]
    public struct MOUSEINPUT
    {
        public int dx;
        public int dy;
        public int mouseData;
        public int dwFlags;
        public int time;
        public IntPtr dwExtraInfo;
    }

            public static class NativeMethods
            {
                [DllImport("user32.dll", SetLastError = true)]
                public static extern uint SendInput(uint nInputs, INPUT[] pInputs, int cbSize);
                [DllImport("user32.dll")]
                public static extern bool SetCursorPos(int X, int Y);
                [DllImport("user32.dll")]
                public static extern void mouse_event(uint dwFlags, int dx, int dy, int dwData, int dwExtraInfo);
                public const uint MOUSEEVENTF_LEFTDOWN = 0x0002;
                public const uint MOUSEEVENTF_LEFTUP = 0x0004;
                public const uint MOUSEEVENTF_WHEEL = 0x0800;
                [DllImport("user32.dll")]
                public static extern bool GetWindowRect(IntPtr hWnd, out RECT lpRect);
                public struct RECT
                {
                    public int Left;
                    public int Top;
                    public int Right;
                    public int Bottom;
                }
            }

            public static class VSCodeChatOcrScroller
            {
                [DllImport("user32.dll")]
                private static extern IntPtr FindWindow(string lpClassName, string lpWindowName);

                [DllImport("user32.dll")]
                private static extern bool SetForegroundWindow(IntPtr hWnd);

                public static void CaptureAndOcrChat(string windowTitle, string outputDir, int scrollSteps = 10, int delayMs = 1000)
                {
                    Directory.CreateDirectory(outputDir);
                    byte[]? lastImageBytes = null;
                    int i = 0;
                    while (true)
                    {
                        var startTime = DateTime.Now;
                        string imgPath = Path.Combine(outputDir, $"chat_capture_{i:D2}.png");
                        bool captured = ScreenCaptureUtility.CaptureWindow(windowTitle, imgPath);
                        if (!captured)
                        {
                            Console.WriteLine($"[ERROR] Could not capture window: '{windowTitle}'. Make sure the window is open and the title matches exactly.");
                            break;
                        }

                        byte[] currentImageBytes = File.ReadAllBytes(imgPath);
                        if (lastImageBytes != null && AreImagesIdentical(lastImageBytes, currentImageBytes))
                        {
                            // Two identical images in a row, stop
                            File.Delete(imgPath); // Optionally delete duplicate
                            break;
                        }
                        lastImageBytes = currentImageBytes;

                        string ocrText = RunEasyOcr(imgPath);
                        File.WriteAllText(Path.Combine(outputDir, $"chat_capture_{i:D2}.txt"), ocrText);

                        SendPageDownToWindow(windowTitle);
                        var elapsed = (DateTime.Now - startTime).TotalMilliseconds;
                        int adaptiveSleep = Math.Max(delayMs - (int)elapsed, 100); // Always sleep at least 100ms
                        Console.WriteLine($"[INFO] Capture {i}: elapsed {elapsed:F0}ms, sleeping {adaptiveSleep}ms");
                        Thread.Sleep(adaptiveSleep);
                        i++;
                    }
                }

                private static bool AreImagesIdentical(byte[] img1, byte[] img2)
                {
                    if (img1.Length != img2.Length)
                        return false;
                    for (int i = 0; i < img1.Length; i++)
                    {
                        if (img1[i] != img2[i])
                            return false;
                    }
                    return true;
                }

                private static void SendPageDownToWindow(string windowTitle)
                {
                    IntPtr hWnd = FindWindow(null, windowTitle);
                    if (hWnd == IntPtr.Zero) return;
                    SetForegroundWindow(hWnd);
                    Thread.Sleep(300); // Allow window to focus
                    // Get window rectangle and click at precise location
                    NativeMethods.RECT rect;
                    if (NativeMethods.GetWindowRect(hWnd, out rect))
                    {
                        int width = rect.Right - rect.Left;
                        int height = rect.Bottom - rect.Top;
                        int x = rect.Left + (int)(width * 0.25); // 25% from left (center of left chat panel)
                        int y = rect.Top + (int)(height * 0.50); // 50% from top (vertically centered)
                        NativeMethods.SetCursorPos(x, y);
                        NativeMethods.mouse_event(NativeMethods.MOUSEEVENTF_LEFTDOWN | NativeMethods.MOUSEEVENTF_LEFTUP, x, y, 0, 0);
                        Thread.Sleep(100); // Allow click to register
                        // Use SendInput for mouse wheel (more reliable)
                        for (int s = 0; s < 10; s++)
                        {
                            INPUT input = new INPUT();
                            input.type = 0; // INPUT_MOUSE
                            input.U.mi = new MOUSEINPUT
                            {
                                dwFlags = 0x0800, // MOUSEEVENTF_WHEEL
                                mouseData = -120, // 1 notch down
                            };
                            NativeMethods.SendInput(1, new INPUT[] { input }, System.Runtime.InteropServices.Marshal.SizeOf(typeof(INPUT)));
                            Thread.Sleep(50);
                        }
                    }
                }

                private static string RunEasyOcr(string imagePath)
                {
                    var psi = new System.Diagnostics.ProcessStartInfo
                    {
                        FileName = "python",
                        Arguments = $"\"d:/Dev library/tools/easyocr_ocr.py\" \"{imagePath}\"",
                        RedirectStandardOutput = true,
                        RedirectStandardError = true,
                        UseShellExecute = false,
                        CreateNoWindow = true
                    };
                    using var proc = System.Diagnostics.Process.Start(psi);
                    string output = proc.StandardOutput.ReadToEnd();
                    proc.WaitForExit();
                    return output;
                }
            }
        }

