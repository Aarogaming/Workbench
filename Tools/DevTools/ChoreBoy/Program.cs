using System.Reflection;
using System.Text.Json;

// Dev-only Functional Test Runner for Project Maelstrom.
// Verifies policy enforcement, executor selection, plugin gating, and failure safety via reflection.

var runner = new TestRunner();
runner.Run();

internal sealed class TestRunner
{
    private readonly List<TestCase> _cases = new();
    private int _pass;
    private int _fail;

    public void Run()
    {
        try
        {
            Setup();
            foreach (var tc in _cases)
            {
                Console.WriteLine($"--- {tc.Name} ---");
                try
                {
                    tc.Action();
                    Console.WriteLine($"[PASS] {tc.Expectation}");
                    _pass++;
                }
                catch (Exception ex)
                {
                    var reason = ex.InnerException?.Message ?? ex.Message;
                    Console.WriteLine($"[FAIL] {tc.Expectation}");
                    Console.WriteLine($"Reason: {reason}");
                    _fail++;
                }
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Runner error: {ex}");
            _fail++;
        }
        finally
        {
            Console.WriteLine("=== Summary ===");
            Console.WriteLine($"Total: {_cases.Count}, Passed: {_pass}, Failed: {_fail}");
        }
    }

    private void Setup()
    {
        var ctx = new ReflectionContext();

        // Clean plugin root for deterministic results
        ctx.CleanPlugins();

        _cases.Add(new TestCase(
            "Policy: Public blocks live",
            "Public profile blocks live execution",
            () =>
            {
                ctx.WritePolicy(allowLive: false, profile: "AcademicSimulation");
                ctx.ReloadPolicy();
                var snap = ctx.GetSnapshot();
                if (snap.allowLive) throw new InvalidOperationException("AllowLiveAutomation should be false");
                if (snap.profile != "AcademicSimulation") throw new InvalidOperationException("Profile should be AcademicSimulation");
                var exec = ctx.CreateExecutor();
                if (exec.type != "SimulationExecutor") throw new InvalidOperationException($"Expected SimulationExecutor, got {exec.type}");
                var result = ctx.Execute(exec.instance, "test", commands: Array.Empty<object>());
                if (result.status != "NoCommands" && result.status != "Simulated")
                    throw new InvalidOperationException($"Expected NoCommands/Simulated, got {result.status}");
            }));

        _cases.Add(new TestCase(
            "Policy: Experimental blocks live",
            "Experimental profile still blocks when AllowLive=false",
            () =>
            {
                ctx.WritePolicy(allowLive: false, profile: "ExperimentalSimulation");
                ctx.ReloadPolicy();
                var snap = ctx.GetSnapshot();
                if (snap.allowLive) throw new InvalidOperationException("AllowLiveAutomation should be false");
                if (snap.profile != "ExperimentalSimulation") throw new InvalidOperationException("Profile should be ExperimentalSimulation");
                var exec = ctx.CreateExecutor();
                if (exec.type != "SimulationExecutor") throw new InvalidOperationException($"Expected SimulationExecutor, got {exec.type}");
                var result = ctx.Execute(exec.instance, "test", commands: Array.Empty<object>());
                if (result.status != "NoCommands" && result.status != "Simulated")
                    throw new InvalidOperationException($"Expected NoCommands/Simulated, got {result.status}");
            }));

        _cases.Add(new TestCase(
            "Policy: Live allowed but no backend",
            "Live enabled returns LiveEnabledNoBackend or LiveDispatched (no crash)",
            () =>
            {
                ctx.WritePolicy(allowLive: true, profile: "ExperimentalSimulation");
                ctx.ReloadPolicy();
                var snap = ctx.GetSnapshot();
                if (!snap.allowLive) throw new InvalidOperationException("AllowLiveAutomation should be true");
                var exec = ctx.CreateExecutor();
                if (exec.type != "LiveExecutor") throw new InvalidOperationException($"Expected LiveExecutor, got {exec.type}");
                var result = ctx.Execute(exec.instance, "test", commands: Array.Empty<object>());
                var ok = result.status == "LiveEnabledNoBackend" || result.status == "LiveDispatched" || result.status == "NoCommands";
                if (!ok) throw new InvalidOperationException($"Expected LiveEnabledNoBackend/LiveDispatched/NoCommands, got {result.status}");
            }));

        _cases.Add(new TestCase(
            "Plugin: SampleOverlay allowed",
            "SampleOverlay allowed in Public profile",
            () =>
            {
                ctx.WritePolicy(allowLive: false, profile: "AcademicSimulation");
                ctx.ReloadPolicy();
                ctx.InstallSampleOverlay();
                ctx.ReloadPlugins();
                var info = ctx.GetPlugin("SampleOverlay");
                if (info == null) throw new InvalidOperationException("SampleOverlay not found");
                if (info.Value.status != "Allowed") throw new InvalidOperationException($"Expected Allowed, got {info.Value.status} ({info.Value.reason})");
            }));

        _cases.Add(new TestCase(
            "Plugin: SampleLiveIntegration blocked",
            "SampleLiveIntegration blocked when live disabled",
            () =>
            {
                ctx.WritePolicy(allowLive: false, profile: "ExperimentalSimulation");
                ctx.ReloadPolicy();
                ctx.InstallSampleLiveIntegration();
                ctx.ReloadPlugins();
                var info = ctx.GetPlugin("SampleLiveIntegration");
                if (info == null) throw new InvalidOperationException("SampleLiveIntegration not found");
                if (info.Value.status != "Blocked") throw new InvalidOperationException($"Expected Blocked, got {info.Value.status} ({info.Value.reason})");
            }));

        _cases.Add(new TestCase(
            "Plugin: Invalid manifest",
            "Corrupt manifest reports Failed or error reason",
            () =>
            {
                ctx.WritePolicy(allowLive: false, profile: "AcademicSimulation");
                ctx.ReloadPolicy();
                ctx.InstallCorruptPlugin();
                ctx.ReloadPlugins();
                var info = ctx.GetPluginStartsWith("CorruptPlugin");
                if (info == null) throw new InvalidOperationException("CorruptPlugin not found");
                if (info.Value.status != "Failed" && !info.Value.reason.Contains("error", StringComparison.OrdinalIgnoreCase))
                {
                    throw new InvalidOperationException($"Expected Failed/error, got {info.Value.status} ({info.Value.reason})");
                }
            }));

        _cases.Add(new TestCase(
            "MinigameCatalog: empty when no plugins",
            "Minigame catalog returns zero entries when no catalog plugins are installed",
            () =>
            {
                ctx.WritePolicy(allowLive: false, profile: "AcademicSimulation");
                ctx.ReloadPolicy();
                ctx.CleanPlugins();
                ctx.ReloadPlugins();
                ctx.ReloadMinigameCatalog();
                var entries = ctx.GetMinigameEntries();
                if (entries.Count != 0) throw new InvalidOperationException($"Expected 0 entries, got {entries.Count}");
            }));

        _cases.Add(new TestCase(
            "MinigameCatalog: loads sample",
            "SampleMinigameCatalog installs and loads entries",
            () =>
            {
                ctx.WritePolicy(allowLive: false, profile: "AcademicSimulation");
                ctx.ReloadPolicy();
                ctx.CleanPlugins();
                ctx.InstallSampleMinigameCatalog();
                ctx.ReloadPlugins();
                ctx.ReloadMinigameCatalog();
                var entries = ctx.GetMinigameEntries();
                if (entries.Count == 0) throw new InvalidOperationException("Expected entries from SampleMinigameCatalog");
            }));

        _cases.Add(new TestCase(
            "MinigameCatalog: blocked plugin yields zero entries",
            "Blocked catalog plugin does not contribute entries",
            () =>
            {
                ctx.WritePolicy(allowLive: false, profile: "AcademicSimulation");
                ctx.ReloadPolicy();
                ctx.CleanPlugins();
                ctx.InstallBlockedMinigameCatalog();
                ctx.ReloadPlugins();
                ctx.ReloadMinigameCatalog();
                var entries = ctx.GetMinigameEntries();
                if (entries.Count != 0) throw new InvalidOperationException($"Expected 0 entries from blocked plugin, got {entries.Count}");
            }));

        _cases.Add(new TestCase(
            "Policy: Corrupt policy fallback",
            "Corrupt policy file falls back to safe defaults",
            () =>
            {
                ctx.WriteCorruptPolicy();
                ctx.ReloadPolicy();
                var snap = ctx.GetSnapshot();
                if (snap.allowLive) throw new InvalidOperationException("Corrupt policy should default to allowLive=false");
                if (snap.profile != "AcademicSimulation") throw new InvalidOperationException("Corrupt policy should default to AcademicSimulation");
            }));
    }
}

internal sealed class TestCase
{
    public string Name { get; }
    public string Expectation { get; }
    public Action Action { get; }
    public TestCase(string name, string expectation, Action action)
    {
        Name = name;
        Expectation = expectation;
        Action = action;
    }
}

internal sealed class ReflectionContext
{
    private readonly Assembly _asm;
    private readonly Type _policyManager;
    private readonly Type _executorFactory;
    private readonly Type _inputCommand;
    private readonly Type _pluginLoader;
    private readonly Type _minigameRegistry;
    private readonly string _policyPath;

    public ReflectionContext()
    {
        var asmPath = Path.Combine(AppContext.BaseDirectory, "ProjectMaelstrom.dll");
        if (!File.Exists(asmPath))
        {
            throw new FileNotFoundException("ProjectMaelstrom.dll not found in output directory", asmPath);
        }
        _asm = Assembly.LoadFrom(asmPath);
        _policyManager = _asm.GetType("ProjectMaelstrom.Utilities.ExecutionPolicyManager")!;
        _executorFactory = _asm.GetType("ProjectMaelstrom.Utilities.ExecutorFactory")!;
        _inputCommand = _asm.GetType("ProjectMaelstrom.Models.InputCommand")!;
        _pluginLoader = _asm.GetType("ProjectMaelstrom.Utilities.PluginLoader")!;
        _minigameRegistry = _asm.GetType("ProjectMaelstrom.Utilities.MinigameCatalogRegistry")!;
        _policyPath = (string)(_policyManager.GetProperty("PolicyPath", BindingFlags.Public | BindingFlags.Static)!.GetValue(null)!);
    }

    public void WritePolicy(bool allowLive, string profile)
    {
        var lines = new[]
        {
            $"ALLOW_LIVE_AUTOMATION={allowLive.ToString().ToLowerInvariant()}",
            $"EXECUTION_PROFILE={profile}"
        };
        File.WriteAllLines(_policyPath, lines);
    }

    public void WriteCorruptPolicy()
    {
        File.WriteAllText(_policyPath, "THIS_IS_NOT_VALID");
    }

    public void ReloadPolicy()
    {
        _policyManager.GetMethod("Reload", BindingFlags.Public | BindingFlags.Static)!.Invoke(null, null);
    }

    public (bool allowLive, string mode, string profile) GetSnapshot()
    {
        var snap = _policyManager.GetProperty("Current", BindingFlags.Public | BindingFlags.Static)!.GetValue(null)!;
        var allow = (bool)snap.GetType().GetProperty("AllowLiveAutomation")!.GetValue(snap)!;
        var mode = snap.GetType().GetProperty("Mode")!.GetValue(snap)!.ToString()!;
        var profile = snap.GetType().GetProperty("Profile")!.GetValue(snap)!.ToString()!;
        return (allow, mode, profile);
    }

    public (object instance, string type) CreateExecutor()
    {
        var snapObj = _policyManager.GetProperty("Current", BindingFlags.Public | BindingFlags.Static)!.GetValue(null)!;
        var exec = _executorFactory.GetMethod("FromPolicy", BindingFlags.Public | BindingFlags.Static)!.Invoke(null, new[] { snapObj })!;
        return (exec, exec.GetType().Name);
    }

    public (string status, string message) Execute(object executor, string source, IEnumerable<object>? commands = null)
    {
        Array? list = null;
        if (commands == null)
        {
            var cmd = Activator.CreateInstance(_inputCommand)!;
            _inputCommand.GetProperty("Type")!.SetValue(cmd, "click");
            list = Array.CreateInstance(_inputCommand, 1);
            list.SetValue(cmd, 0);
        }
        else
        {
            var cmdList = commands
                .Where(c => c != null)
                .Select(c =>
                {
                    if (c is Array a && a.Length > 0) return a.GetValue(0);
                    return c;
                })
                .Where(c => c != null)
                .ToList();
            if (cmdList.Count == 0)
            {
                list = Array.CreateInstance(_inputCommand, 0);
            }
            else
            {
                list = Array.CreateInstance(_inputCommand, cmdList.Count);
                for (int i = 0; i < cmdList.Count; i++)
                {
                    list.SetValue(cmdList[i], i);
                }
            }
        }

        var ctxType = _asm.GetType("ProjectMaelstrom.Utilities.ExecutionContext")!;
        var ctx = Activator.CreateInstance(ctxType)!;
        ctxType.GetProperty("Source")!.SetValue(ctx, source);

        var result = executor.GetType().GetMethod("Execute")!.Invoke(executor, new object?[] { list, ctx })!;
        var status = result.GetType().GetProperty("Status")!.GetValue(result)!.ToString()!;
        var message = result.GetType().GetProperty("Message")!.GetValue(result)?.ToString() ?? "";
        return (status, message);
    }

    public void CleanPlugins()
    {
        var pluginRoot = (string)_pluginLoader.GetProperty("PluginRoot", BindingFlags.Public | BindingFlags.Static)!.GetValue(null)!;
        if (Directory.Exists(pluginRoot))
        {
            Directory.Delete(pluginRoot, true);
        }
    }

    public void ReloadPlugins()
    {
        _pluginLoader.GetMethod("Reload", BindingFlags.Public | BindingFlags.Static)!.Invoke(null, null);
        // Force ensure load by reading Current
        _ = _pluginLoader.GetProperty("Current", BindingFlags.Public | BindingFlags.Static)!.GetValue(null);
    }

    public void InstallSampleOverlay()
    {
        var pluginRoot = (string)_pluginLoader.GetProperty("PluginRoot", BindingFlags.Public | BindingFlags.Static)!.GetValue(null)!;
        var samplesRoot = Path.Combine(pluginRoot, "_samples");
        Directory.CreateDirectory(samplesRoot);
        var manifest = new
        {
            pluginId = "SampleOverlay",
            name = "SampleOverlay",
            version = "1.0.0",
            targetAppVersion = "any",
            requiredProfile = "Public",
            declaredCapabilities = new[] { "OverlayWidgets" }
        };
        File.WriteAllText(Path.Combine(samplesRoot, "SampleOverlay.manifest.json"), JsonSerializer.Serialize(manifest));
    }

    public void InstallSampleLiveIntegration()
    {
        var pluginRoot = (string)_pluginLoader.GetProperty("PluginRoot", BindingFlags.Public | BindingFlags.Static)!.GetValue(null)!;
        var samplesRoot = Path.Combine(pluginRoot, "_samples");
        Directory.CreateDirectory(samplesRoot);
        var manifest = new
        {
            pluginId = "SampleLiveIntegration",
            name = "SampleLiveIntegration",
            version = "1.0.0",
            targetAppVersion = "any",
            requiredProfile = "Experimental",
            declaredCapabilities = new[] { "LiveIntegration" }
        };
        File.WriteAllText(Path.Combine(samplesRoot, "SampleLiveIntegration.manifest.json"), JsonSerializer.Serialize(manifest));
    }

    public void InstallCorruptPlugin()
    {
        var pluginRoot = (string)_pluginLoader.GetProperty("PluginRoot", BindingFlags.Public | BindingFlags.Static)!.GetValue(null)!;
        var samplesRoot = Path.Combine(pluginRoot, "_samples");
        Directory.CreateDirectory(samplesRoot);
        File.WriteAllText(Path.Combine(samplesRoot, "CorruptPlugin.manifest.json"), "{ this is not valid json }");
    }

    public void InstallSampleMinigameCatalog()
    {
        var pluginRoot = (string)_pluginLoader.GetProperty("PluginRoot", BindingFlags.Public | BindingFlags.Static)!.GetValue(null)!;
        var samplesRoot = Path.Combine(pluginRoot, "_samples");
        var pluginDir = Path.Combine(samplesRoot, "SampleMinigameCatalog");
        Directory.CreateDirectory(pluginDir);
        var manifest = new
        {
            pluginId = "SampleMinigameCatalog",
            name = "SampleMinigameCatalog",
            version = "1.0.0",
            targetAppVersion = "any",
            requiredProfile = "Public",
            declaredCapabilities = new[] { "MinigameCatalog" }
        };
        File.WriteAllText(Path.Combine(pluginDir, "plugin.manifest.json"), JsonSerializer.Serialize(manifest));

        var catalog = new[]
        {
            new {
                id = "pet-dance",
                name = "Pet Dance",
                category = 0, // MinigameCategory.Pet
                status = 0,   // MinigameStatus.Planned
                description = "Sample planned entry for tests."
            }
        };
        File.WriteAllText(Path.Combine(pluginDir, "minigames.catalog.json"), JsonSerializer.Serialize(catalog));
    }

    public void InstallBlockedMinigameCatalog()
    {
        var pluginRoot = (string)_pluginLoader.GetProperty("PluginRoot", BindingFlags.Public | BindingFlags.Static)!.GetValue(null)!;
        var samplesRoot = Path.Combine(pluginRoot, "_samples");
        var pluginDir = Path.Combine(samplesRoot, "BlockedMinigameCatalog");
        Directory.CreateDirectory(pluginDir);
        var manifest = new
        {
            pluginId = "BlockedMinigameCatalog",
            name = "BlockedMinigameCatalog",
            version = "1.0.0",
            targetAppVersion = "any",
            requiredProfile = "Experimental",
            declaredCapabilities = new[] { "MinigameCatalog" }
        };
        File.WriteAllText(Path.Combine(pluginDir, "plugin.manifest.json"), JsonSerializer.Serialize(manifest));

        var catalog = new[]
        {
            new {
                id = "blocked-entry",
                name = "Blocked Entry",
                category = 3, // MinigameCategory.Other
                status = 0,   // MinigameStatus.Planned
                description = "Should not load when profile is AcademicSimulation."
            }
        };
        File.WriteAllText(Path.Combine(pluginDir, "minigames.catalog.json"), JsonSerializer.Serialize(catalog));
    }

    public (string status, string reason)? GetPlugin(string id)
    {
        var list = (IEnumerable<object>)_pluginLoader.GetProperty("Current", BindingFlags.Public | BindingFlags.Static)!.GetValue(null)!;
        foreach (var p in list)
        {
            var pid = p.GetType().GetProperty("PluginId")!.GetValue(p)?.ToString();
            if (string.Equals(pid, id, StringComparison.OrdinalIgnoreCase))
            {
                var status = p.GetType().GetProperty("Status")!.GetValue(p)!.ToString()!;
                var reason = p.GetType().GetProperty("Reason")!.GetValue(p)?.ToString() ?? "";
                return (status, reason);
            }
        }
        return null;
    }

    public (string status, string reason)? GetPluginStartsWith(string prefix)
    {
        var list = (IEnumerable<object>)_pluginLoader.GetProperty("Current", BindingFlags.Public | BindingFlags.Static)!.GetValue(null)!;
        foreach (var p in list)
        {
            var pid = p.GetType().GetProperty("PluginId")!.GetValue(p)?.ToString() ?? "";
            if (pid.StartsWith(prefix, StringComparison.OrdinalIgnoreCase))
            {
                var status = p.GetType().GetProperty("Status")!.GetValue(p)!.ToString()!;
                var reason = p.GetType().GetProperty("Reason")!.GetValue(p)?.ToString() ?? "";
                return (status, reason);
            }
        }
        return null;
    }

    public void ReloadMinigameCatalog()
    {
        _minigameRegistry.GetMethod("Reload", BindingFlags.Public | BindingFlags.Static)!.Invoke(null, null);
    }

    public List<object> GetMinigameEntries()
    {
        var current = _minigameRegistry.GetProperty("Current", BindingFlags.Public | BindingFlags.Static)!.GetValue(null);
        if (current is System.Collections.IEnumerable enumerable)
        {
            var list = new List<object>();
            foreach (var item in enumerable) list.Add(item!);
            return list;
        }
        return new List<object>();
    }
}
