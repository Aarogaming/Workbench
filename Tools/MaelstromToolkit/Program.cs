using System.Reflection;
using System.Text;
using System.Text.Json;
using Json.Schema;

namespace MaelstromToolkit;

internal static class Program
{
    private record CommandOptions(
        string Command,
        string Subcommand,
        Dictionary<string, string> Args,
        bool Force,
        bool DryRun,
        bool Verbose,
        bool ShowHelp,
        bool ShowVersion);

    private static int Main(string[] args)
    {
        var options = Parse(args);
        if (options == null || options.ShowHelp)
        {
            PrintUsage();
            return options == null ? 1 : 0;
        }

        if (options.ShowVersion)
        {
            Console.WriteLine(GetVersion());
            return 0;
        }

        var root = options.Args.TryGetValue("out", out var outDir)
            ? Path.GetFullPath(outDir)
            : Directory.GetCurrentDirectory();

        var summary = new List<string>();
        var warnings = new List<string>();

        try
        {
            if (RequiresOut(options.Command) && !options.Args.ContainsKey("out"))
            {
                Console.Error.WriteLine("ERROR: --out <dir> is required for this command.");
                return 1;
            }
            if (RequiresOut(options.Command) && !ValidateOut(root, options))
            {
                return 2;
            }

            Console.WriteLine($"MaelstromToolkit {GetVersion()} | command={options.Command} {options.Subcommand}".Trim());

            switch (options.Command)
            {
                case "init":
                    RunInit(root, options, summary, warnings);
                    break;
                case "policy" when options.Subcommand == "init":
                    CopyTemplate(root, "POLICY_BOUNDARY.md", options, summary, warnings);
                    CopyTemplate(root, "policy.config.sample", options, summary, warnings);
                    break;
                case "tags" when options.Subcommand == "init":
                    CopyTemplate(root, "TAG_POLICY.md", options, summary, warnings);
                    break;
                case "stewardship" when options.Subcommand == "init":
                    CopyTemplate(root, "STEWARDSHIP_CHECKLIST.md", options, summary, warnings);
                    CopyTemplate(root, "FEEDBACK_LOG.md", options, summary, warnings);
                    break;
                case "ux" when options.Subcommand == "init":
                    var framework = options.Args.TryGetValue("framework", out var fw) ? fw : "winforms";
                    CopyTemplate(root, "UX_MAINTENANCE.md", options, summary, warnings);
                    CopyTemplate(root, "UX_STYLE_GUIDE.md", options, summary, warnings, framework);
                    CopyTemplate(root, "UX_CHANGELOG.md", options, summary, warnings, framework);
                    CopyTemplate(root, "UX_TOKENS.md", options, summary, warnings, framework);
                    break;
                case "ci" when options.Subcommand == "add":
                    var provider = options.Args.TryGetValue("provider", out var p) ? p : "github";
                    var profile = options.Args.TryGetValue("profile", out var pr) ? pr : "tools-only";
                    CopyTemplate(root, $"{provider}_{profile}_workflow.yml", options, summary, warnings);
                    break;
                case "guild":
                    CopyTemplate(root, "README.md", options, summary, warnings);
                    break;
                case "contracts" when options.Subcommand == "validate":
                    return RunContractsValidate(options);
                case "contracts" when options.Subcommand == "checkfile":
                    return RunContractsCheckFile(options);
                case "selftest":
                    return RunSelftest(options, summary, warnings);
                default:
                    PrintUsage();
                    return 1;
            }
        }
        catch (Exception ex)
        {
            Console.Error.WriteLine($"ERROR: {ex.Message}");
            return 1;
        }

        if (summary.Count > 0)
        {
            Console.WriteLine("Generated:");
            foreach (var line in summary) Console.WriteLine($"- {line}");
        }
        if (warnings.Count > 0)
        {
            Console.WriteLine("Warnings:");
            foreach (var line in warnings) Console.WriteLine($"- {line}");
        }

        return 0;
    }

    private static int RunContractsValidate(CommandOptions options)
    {
        var root = options.Args.TryGetValue("root", out var r)
            ? Path.GetFullPath(r)
            : Directory.GetCurrentDirectory();

        var schemaDir = Path.Combine(root, "contracts", "schema");
        var examplesDir = Path.Combine(root, "contracts", "examples");

        if (!Directory.Exists(schemaDir))
        {
            Console.Error.WriteLine($"ERROR: schema dir not found: {schemaDir}");
            return 2;
        }
        if (!Directory.Exists(examplesDir))
        {
            Console.Error.WriteLine($"ERROR: examples dir not found: {examplesDir}");
            return 2;
        }

        // Register all schemas once so $ref works.
        var registry = new SchemaRegistry();
        var schemasByFile = new Dictionary<string, JsonSchema>(StringComparer.OrdinalIgnoreCase);
        foreach (var schemaPath in Directory.GetFiles(schemaDir, "*.schema.json", SearchOption.AllDirectories))
        {
            var schemaJson = File.ReadAllText(schemaPath);
            var schema = JsonSchema.FromText(schemaJson);
            registry.Register(schema);
            schemasByFile[Path.GetFileName(schemaPath)] = schema;
        }

        int failures = 0;
        foreach (var examplePath in Directory.GetFiles(examplesDir, "*.sample.json", SearchOption.AllDirectories))
        {
            try
            {
                using var doc = JsonDocument.Parse(File.ReadAllText(examplePath));
                if (!doc.RootElement.TryGetProperty("schemaName", out var nameProp) || nameProp.ValueKind != JsonValueKind.String)
                {
                    Console.Error.WriteLine($"FAIL {examplePath}: missing schemaName");
                    failures++;
                    continue;
                }

                string schemaName = nameProp.GetString() ?? string.Empty;
                string schemaFileStem = schemaName switch
                {
                    "CommandBatch" => "command-batch.v1.schema.json",
                    "GameStateSnapshot" => "snapshot.v1.schema.json",
                    "HandoffEnvelope" => "handoff-envelope.v1.schema.json",
                    "ContractsIndex" => "contracts-index.v1.schema.json",
                    "HomeDeviceControl" => "home-device-control.v1.schema.json",
                    "Capability" => "capability.v1.schema.json",
                    "PluginManifest" => "plugin-manifest.v1.schema.json",
                    "EventEnvelope" => "event-envelope.v1.schema.json",
                    "MeshCapabilityAdvertisement" => "mesh-capability-advertisement.v1.schema.json",
                    "SwarmMembershipHeartbeat" => "swarm-membership-heartbeat.v1.schema.json",
                    "SwarmProviderAssignment" => "swarm-provider-assignment.v1.schema.json",
                    _ => string.Empty
                };

                if (string.IsNullOrWhiteSpace(schemaFileStem))
                {
                    Console.Error.WriteLine($"FAIL {examplePath}: unknown schemaName '{schemaName}'");
                    failures++;
                    continue;
                }

                if (!schemasByFile.TryGetValue(schemaFileStem, out var schema))
                {
                    Console.Error.WriteLine($"FAIL {examplePath}: schema file not found: {schemaFileStem}");
                    failures++;
                    continue;
                }

                var eval = schema.Evaluate(doc.RootElement, new EvaluationOptions
                {
                    OutputFormat = OutputFormat.List
                });

                if (!eval.IsValid)
                {
                    Console.Error.WriteLine($"FAIL {examplePath}: does not validate against {schemaFileStem}");
                    if (eval.Details is not null)
                    {
                        foreach (var detail in eval.Details)
                        {
                            if (detail == null) continue;
                            if (detail.IsValid) continue;
                            Console.Error.WriteLine($"  - {detail.InstanceLocation}");
                        }
                    }
                    failures++;
                }
                else if (options.Verbose)
                {
                    Console.WriteLine($"OK   {examplePath}");
                }
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine($"FAIL {examplePath}: {ex.Message}");
                failures++;
            }
        }

        if (failures > 0)
        {
            Console.Error.WriteLine($"Contracts validation failed: {failures} file(s)");
            return 1;
        }

        Console.WriteLine("Contracts validation OK");
        return 0;
    }

    private static int RunContractsCheckFile(CommandOptions options)
    {
        if (!options.Args.TryGetValue("root", out var rootArg) || string.IsNullOrWhiteSpace(rootArg))
        {
            Console.Error.WriteLine("ERROR: --root <aas-hub-root> is required");
            return 2;
        }
        if (!options.Args.TryGetValue("schema", out var schemaArg) || string.IsNullOrWhiteSpace(schemaArg))
        {
            Console.Error.WriteLine("ERROR: --schema <schema-file> is required (e.g. command-batch.v1.schema.json)");
            return 2;
        }
        if (!options.Args.TryGetValue("file", out var fileArg) || string.IsNullOrWhiteSpace(fileArg))
        {
            Console.Error.WriteLine("ERROR: --file <path-to-json> is required");
            return 2;
        }

        var root = Path.GetFullPath(rootArg);
        var schemaDir = Path.Combine(root, "contracts", "schema");
        var schemaPath = Path.Combine(schemaDir, schemaArg);
        var jsonPath = Path.GetFullPath(fileArg);

        if (!File.Exists(schemaPath))
        {
            Console.Error.WriteLine($"ERROR: schema not found: {schemaPath}");
            return 2;
        }
        if (!File.Exists(jsonPath))
        {
            Console.Error.WriteLine($"ERROR: json file not found: {jsonPath}");
            return 2;
        }

        // NOTE: JsonSchema.Net maintains internal global registration keyed by $id.
        // To keep this command safe to call repeatedly, avoid registering every schema each run.
        // Cross-schema $ref support is handled by `contracts validate` (examples), while `checkfile`
        // focuses on validating a concrete payload against a concrete schema.
        var schema = JsonSchema.FromText(File.ReadAllText(schemaPath));
        using var doc = JsonDocument.Parse(File.ReadAllText(jsonPath));
        var eval = schema.Evaluate(doc.RootElement, new EvaluationOptions { OutputFormat = OutputFormat.List });

        if (eval.IsValid)
        {
            return 0;
        }

        Console.Error.WriteLine($"FAIL {jsonPath}: does not validate against {schemaArg}");
        if (eval.Details is not null)
        {
            foreach (var detail in eval.Details)
            {
                if (detail == null) continue;
                if (detail.IsValid) continue;
                Console.Error.WriteLine($"  - {detail.InstanceLocation}");
            }
        }

        return 1;
    }

    private static CommandOptions? Parse(string[] args)
    {
        if (args.Length == 0) return null;
        var showHelp = args.Contains("--help", StringComparer.OrdinalIgnoreCase);
        var showVersion = args.Contains("--version", StringComparer.OrdinalIgnoreCase);
        string? command = null;
        string sub = string.Empty;
        var dict = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase);
        var force = args.Contains("--force", StringComparer.OrdinalIgnoreCase);
        var dryRun = args.Contains("--dry-run", StringComparer.OrdinalIgnoreCase);
        var verbose = args.Contains("--verbose", StringComparer.OrdinalIgnoreCase);

        foreach (var arg in args)
        {
            if (arg.StartsWith("--", StringComparison.Ordinal)) continue;
            if (command == null)
            {
                command = arg;
            }
            else if (string.IsNullOrEmpty(sub))
            {
                sub = arg;
            }
        }

        for (var i = 0; i < args.Length; i++)
        {
            if (!args[i].StartsWith("--", StringComparison.Ordinal)) continue;
            var key = args[i][2..];
            if (key is "force" or "dry-run" or "verbose" or "help" or "version") continue;
            if (i + 1 < args.Length && !args[i + 1].StartsWith("--", StringComparison.Ordinal))
            {
                dict[key] = args[i + 1];
            }
        }

        if (string.IsNullOrWhiteSpace(command)) return null;
        return new CommandOptions(command, sub, dict, force, dryRun, verbose, showHelp, showVersion);
    }

    private static void PrintUsage()
    {
        Console.WriteLine("MaelstromToolkit (net8.0) - safe, deterministic scaffolds");
        Console.WriteLine("Usage (examples):");
        Console.WriteLine("  maelstromtoolkit init --out ./out");
        Console.WriteLine("  maelstromtoolkit policy init --out ./out");
        Console.WriteLine("  maelstromtoolkit tags init --out ./out");
        Console.WriteLine("  maelstromtoolkit stewardship init --out ./out");
        Console.WriteLine("  maelstromtoolkit ux init --framework winforms --out ./out");
        Console.WriteLine("  maelstromtoolkit ci add --provider github --profile tools-only --out ./out");
        Console.WriteLine("  maelstromtoolkit guild --out ./out");
        Console.WriteLine("  maelstromtoolkit contracts validate --root <aas-hub-root>");
        Console.WriteLine("  maelstromtoolkit contracts checkfile --root <aas-hub-root> --schema <schema-file> --file <json-file>");
        Console.WriteLine("  maelstromtoolkit selftest");
        Console.WriteLine("Flags: --force (overwrite), --dry-run, --verbose, --help, --version, --out <dir>");
    }

    private static void RunInit(string root, CommandOptions options, List<string> summary, List<string> warnings)
    {
        CopyTemplate(root, "POLICY_BOUNDARY.md", options, summary, warnings);
        CopyTemplate(root, "policy.config.sample", options, summary, warnings);
        CopyTemplate(root, "TAG_POLICY.md", options, summary, warnings);
        CopyTemplate(root, "STEWARDSHIP_CHECKLIST.md", options, summary, warnings);
        CopyTemplate(root, "FEEDBACK_LOG.md", options, summary, warnings);
        CopyTemplate(root, "UX_MAINTENANCE.md", options, summary, warnings);
    }

    private static void CopyTemplate(string targetRoot, string templateName, CommandOptions options, List<string> summary, List<string> warnings, string? framework = null)
    {
        var source = Path.Combine(AppContext.BaseDirectory, "Templates", templateFolderFor(templateName), templateName);
        if (!File.Exists(source))
        {
            warnings.Add($"Template missing: {templateName}");
            return;
        }
        var content = File.ReadAllText(source);
        if (!string.IsNullOrWhiteSpace(framework))
        {
            content = content.Replace("{{FRAMEWORK}}", framework, StringComparison.OrdinalIgnoreCase);
        }
        var dest = Path.Combine(targetRoot, templateName);
        if (File.Exists(dest) && !options.Force)
        {
            warnings.Add($"Skipped existing file: {dest}");
            return;
        }
        WriteFile(dest, content, options, summary, File.Exists(dest));
    }

    private static int RunSelftest(CommandOptions options, List<string> summary, List<string> warnings)
    {
        var templates = new[]
        {
            ("Policy","POLICY_BOUNDARY.md"),
            ("Policy","policy.config.sample"),
            ("Tags","TAG_POLICY.md"),
            ("Stewardship","STEWARDSHIP_CHECKLIST.md"),
            ("Stewardship","FEEDBACK_LOG.md"),
            ("UX","UX_MAINTENANCE.md"),
            ("UX","UX_STYLE_GUIDE.md"),
            ("UX","UX_CHANGELOG.md"),
            ("UX","UX_TOKENS.md"),
            ("CI","github_tools-only_workflow.yml"),
            ("Guild","README.md"),
        };

        var schemaVersion = Path.Combine(AppContext.BaseDirectory, "Templates", "schema_version.txt");
        var manifest = Path.Combine(AppContext.BaseDirectory, "Templates", "manifest.json");
        if (!File.Exists(schemaVersion))
        {
            Console.Error.WriteLine("SELFTEST FAIL: missing schema_version.txt");
            return 1;
        }
        if (!File.Exists(manifest))
        {
            Console.Error.WriteLine("SELFTEST FAIL: missing manifest.json");
            return 1;
        }

        foreach (var (folder, name) in templates)
        {
            var path = Path.Combine(AppContext.BaseDirectory, "Templates", folder, name);
            if (!File.Exists(path))
            {
                Console.Error.WriteLine($"SELFTEST FAIL: missing template {folder}/{name}");
                return 1;
            }
        }

        var tempDir = Path.Combine(Path.GetTempPath(), $"maelstromtoolkit_selftest_{Guid.NewGuid():N}");
        Directory.CreateDirectory(tempDir);
        var testOptions = options with { Force = false };
        CopyTemplate(tempDir, "POLICY_BOUNDARY.md", testOptions, summary, warnings);
        CopyTemplate(tempDir, "policy.config.sample", testOptions, summary, warnings);
        CopyTemplate(tempDir, "TAG_POLICY.md", testOptions, summary, warnings);
        CopyTemplate(tempDir, "STEWARDSHIP_CHECKLIST.md", testOptions, summary, warnings);
        CopyTemplate(tempDir, "FEEDBACK_LOG.md", testOptions, summary, warnings);
        CopyTemplate(tempDir, "UX_MAINTENANCE.md", testOptions, summary, warnings, "winforms");
        CopyTemplate(tempDir, "UX_STYLE_GUIDE.md", testOptions, summary, warnings, "winforms");
        CopyTemplate(tempDir, "UX_CHANGELOG.md", testOptions, summary, warnings, "winforms");
        CopyTemplate(tempDir, "UX_TOKENS.md", testOptions, summary, warnings, "winforms");
        CopyTemplate(tempDir, "github_tools-only_workflow.yml", testOptions, summary, warnings);
        CopyTemplate(tempDir, "README.md", testOptions, summary, warnings);

        try { Directory.Delete(tempDir, true); } catch { /* ignore */ }

        Console.WriteLine("SELFTEST PASS");
        return 0;
    }

    private static void WriteFile(string path, string content, CommandOptions options, List<string> summary, bool existed)
    {
        Directory.CreateDirectory(Path.GetDirectoryName(path)!);
        var utf8 = new UTF8Encoding(encoderShouldEmitUTF8Identifier: false);
        var tmp = path + ".tmp";
        File.WriteAllText(tmp, NormalizeLineEndings(content), utf8);
        if (options.DryRun)
        {
            File.Delete(tmp);
            summary.Add($"(dry-run) {(existed ? "would overwrite" : "would create")} {path}");
            return;
        }
        File.Move(tmp, path, overwrite: true);
        summary.Add(path);
        if (options.Verbose)
        {
            Console.WriteLine($"Wrote {path}");
        }
    }

    private static string NormalizeLineEndings(string input) =>
        input.Replace("\r\n", "\n", StringComparison.Ordinal).Replace("\r", "\n", StringComparison.Ordinal);

    private static string GetVersion() =>
        Assembly.GetExecutingAssembly().GetCustomAttribute<AssemblyInformationalVersionAttribute>()?.InformationalVersion ?? "unknown";

    private static string templateFolderFor(string templateName)
    {
        if (templateName.EndsWith(".yml", StringComparison.OrdinalIgnoreCase)) return "CI";
        if (templateName.Contains("POLICY", StringComparison.OrdinalIgnoreCase) || templateName.Contains("policy", StringComparison.OrdinalIgnoreCase)) return "Policy";
        if (templateName.Contains("TAG", StringComparison.OrdinalIgnoreCase)) return "Tags";
        if (templateName.Contains("FEEDBACK", StringComparison.OrdinalIgnoreCase) || templateName.Contains("STEWARDSHIP", StringComparison.OrdinalIgnoreCase)) return "Stewardship";
        if (templateName.StartsWith("UX_", StringComparison.OrdinalIgnoreCase) || templateName.StartsWith("UX ", StringComparison.OrdinalIgnoreCase) || templateName.Contains("UX", StringComparison.OrdinalIgnoreCase)) return "UX";
        if (templateName.Equals("README.md", StringComparison.OrdinalIgnoreCase)) return "Guild";
        return string.Empty;
    }

    private static bool RequiresOut(string command) =>
        command is "init" or "policy" or "tags" or "stewardship" or "ux" or "ci" or "guild";

    private static bool ValidateOut(string outPath, CommandOptions options)
    {
        var full = Path.GetFullPath(outPath);
        var root = Path.GetPathRoot(full);
        if (string.Equals(full.TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar),
                root?.TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar),
                StringComparison.OrdinalIgnoreCase))
        {
            Console.Error.WriteLine("ERROR: --out cannot be a filesystem root.");
            return false;
        }
        if (IsSymlink(full))
        {
            Console.Error.WriteLine("ERROR: --out cannot be a symlinked directory.");
            return false;
        }
        if (options.Verbose)
        {
            Console.WriteLine($"Using output directory: {full}");
        }
        return true;
    }

    private static bool IsSymlink(string path)
    {
        var dirInfo = new DirectoryInfo(path);
        if (!dirInfo.Exists) return false;
        return dirInfo.Attributes.HasFlag(FileAttributes.ReparsePoint);
    }
}
