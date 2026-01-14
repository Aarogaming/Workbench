using System;
using System.Drawing;
using System.Threading;
using System.Windows.Forms;
using System.IO;

namespace ProjectMaelstrom.Tools
{
    public static class VSCodeChatOcrScroller
    {
        [System.Runtime.InteropServices.DllImport("user32.dll")]
        private static extern IntPtr FindWindow(string lpClassName, string lpWindowName);

        [System.Runtime.InteropServices.DllImport("user32.dll")]
        private static extern bool SetForegroundWindow(IntPtr hWnd);

        public static void CaptureAndOcrChat(string windowTitle, string outputDir, int scrollSteps = 10, int delayMs = 1000)
        {
            Directory.CreateDirectory(outputDir);
            for (int i = 0; i < scrollSteps; i++)
            {
                string imgPath = Path.Combine(outputDir, $"chat_capture_{i:D2}.png");
                bool captured = ScreenCaptureUtility.CaptureWindow(windowTitle, imgPath);
                if (captured)
                {
                    // Call EasyOCR Python script directly
                    string ocrText = RunEasyOcr(imgPath);
                    File.WriteAllText(Path.Combine(outputDir, $"chat_capture_{i:D2}.txt"), ocrText);
                }
                // Simulate scroll: send PageDown key to VS Code window
                SendPageDownToWindow(windowTitle);
                Thread.Sleep(delayMs);
            }
        }

        private static void SendPageDownToWindow(string windowTitle)
        {
            IntPtr hWnd = FindWindow(null, windowTitle);
            if (hWnd == IntPtr.Zero) return;
            SetForegroundWindow(hWnd);
            SendKeys.SendWait("{PGDN}");
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
