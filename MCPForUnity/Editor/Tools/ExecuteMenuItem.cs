using System;
using System.Collections.Generic;
using MCPForUnity.Editor.Helpers;
using Newtonsoft.Json.Linq;
using UnityEditor;

namespace MCPForUnity.Editor.Tools
{
    [McpForUnityTool("execute_menu_item", AutoRegister = false)]
    /// <summary>
    /// Tool to execute a Unity Editor menu item by its path.
    /// </summary>
    public static class ExecuteMenuItem
    {
        // Basic blacklist to prevent execution of disruptive menu items.
        private static readonly HashSet<string> _menuPathBlacklist = new HashSet<string>(
            StringComparer.OrdinalIgnoreCase)
        {
            "File/Quit",
        };

        // Prefer TMP-based uGUI creation when callers use legacy menu paths.
        // Unity keeps these menu labels stable across versions:
        // Text/Button/Dropdown/Input Field + " - TextMeshPro".
        private static readonly Dictionary<string, string> LegacyUguiToTmpMenuPathMap = new(
            StringComparer.OrdinalIgnoreCase)
        {
            { "GameObject/UI/Text", "GameObject/UI/Text - TextMeshPro" },
            { "GameObject/UI/Button", "GameObject/UI/Button - TextMeshPro" },
            { "GameObject/UI/Dropdown", "GameObject/UI/Dropdown - TextMeshPro" },
            { "GameObject/UI/Input Field", "GameObject/UI/Input Field - TextMeshPro" },
            { "GameObject/UI/Legacy/Text", "GameObject/UI/Text - TextMeshPro" },
            { "GameObject/UI/Legacy/Button", "GameObject/UI/Button - TextMeshPro" },
            { "GameObject/UI/Legacy/Dropdown", "GameObject/UI/Dropdown - TextMeshPro" },
            { "GameObject/UI/Legacy/Input Field", "GameObject/UI/Input Field - TextMeshPro" },
        };

        public static object HandleCommand(JObject @params)
        {
            McpLog.Info("[ExecuteMenuItem] Handling menu item command");
            string menuPath = @params["menu_path"]?.ToString() ?? @params["menuPath"]?.ToString();
            if (string.IsNullOrWhiteSpace(menuPath))
            {
                return new ErrorResponse("Required parameter 'menu_path' or 'menuPath' is missing or empty.");
            }
            menuPath = menuPath.Trim();

            if (_menuPathBlacklist.Contains(menuPath))
            {
                return new ErrorResponse($"Execution of menu item '{menuPath}' is blocked for safety reasons.");
            }

            try
            {
                string remappedPath = RemapLegacyUguiMenuPath(menuPath);
                bool wasRemapped = !string.Equals(remappedPath, menuPath, StringComparison.OrdinalIgnoreCase);
                bool executed = EditorApplication.ExecuteMenuItem(remappedPath);

                // TMP menu path may not exist on projects without TMP package/import.
                // In that case, fall back to the original user-supplied path.
                if (!executed && wasRemapped)
                {
                    McpLog.Warn(
                        $"[ExecuteMenuItem] TMP remap '{menuPath}' -> '{remappedPath}' failed. Falling back to original path.");
                    executed = EditorApplication.ExecuteMenuItem(menuPath);
                }

                if (!executed)
                {
                    McpLog.Error(
                        $"[MenuItemExecutor] Failed to execute menu item '{menuPath}' (remapped attempt: '{remappedPath}'). It might be invalid, disabled, or context-dependent.");
                    return new ErrorResponse(
                        $"Failed to execute menu item '{menuPath}' (remapped attempt: '{remappedPath}'). It might be invalid, disabled, or context-dependent.");
                }

                if (wasRemapped)
                {
                    return new SuccessResponse(
                        $"Executed menu item '{remappedPath}' (remapped from '{menuPath}') to prefer TextMeshPro-based uGUI controls.");
                }

                return new SuccessResponse($"Attempted to execute menu item: '{menuPath}'. Check Unity logs for confirmation or errors.");
            }
            catch (Exception e)
            {
                McpLog.Error($"[MenuItemExecutor] Failed to setup execution for '{menuPath}': {e}");
                return new ErrorResponse($"Error setting up execution for menu item '{menuPath}': {e.Message}");
            }
        }

        private static string RemapLegacyUguiMenuPath(string menuPath)
        {
            if (LegacyUguiToTmpMenuPathMap.TryGetValue(menuPath, out string mappedPath))
            {
                return mappedPath;
            }

            return menuPath;
        }
    }
}
