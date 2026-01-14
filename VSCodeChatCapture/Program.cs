using System;

namespace VSCodeChatCapture
{
    internal static class Program
    {
        [STAThread]
        static void Main(string[] args)
        {
            string windowTitle = args.Length > 0 ? args[0] : null;
            string outputDir = args.Length > 1 ? args[1] : "chat_ocr_output";
            int scrollSteps = args.Length > 2 ? int.Parse(args[2]) : 10;
            int delayMs = args.Length > 3 ? int.Parse(args[3]) : 1000;

            if (windowTitle == null)
            {
                // Find VS Code process
                var processes = System.Diagnostics.Process.GetProcessesByName("Code");
                if (processes.Length == 0)
                {
                    Console.WriteLine("[ERROR] VS Code process not found. Please open VS Code.");
                    return;
                }
                var codeProc = processes[0];
                // Find window title for this PID
                windowTitle = FindWindowTitleForPid(codeProc.Id);
                if (windowTitle == null)
                {
                    Console.WriteLine("[ERROR] Could not find VS Code window for PID " + codeProc.Id);
                    return;
                }
                Console.WriteLine($"Auto-detected VS Code window title: '{windowTitle}'");
            }

            VSCodeChatOcrScroller.CaptureAndOcrChat(windowTitle, outputDir, scrollSteps, delayMs);
            Console.WriteLine($"Done. Output in {outputDir}");

        }

        // Helper to find window title for a given PID
        static string? FindWindowTitleForPid(int pid)
        {
            string? foundTitle = null;
            foreach (var p in System.Diagnostics.Process.GetProcesses())
            {
                if (p.Id == pid && !string.IsNullOrEmpty(p.MainWindowTitle))
                {
                    foundTitle = p.MainWindowTitle;
                    break;
                }
            }
            return foundTitle;
        }
    }
}
