# Shortcuts

Shortcuts let you quickly copy all settings from one PG service to another. This is useful when you regularly overwrite a service definition — for example, pointing your `production` service to a `staging` configuration for testing, then switching it back.

Once created, shortcuts are accessible from the plugin **toolbar button** dropdown and from the **Database** menu, so you can execute them without even opening the dialog.

## Creating a shortcut

1. Open the plugin dialog and go to the **Shortcuts** tab.
2. Click the **+** button to add a new shortcut.
3. In the **From** column, select the source service from the dropdown.
4. In the **To** column, select the target service from the dropdown.
5. The **Name** column is auto-filled as `"source → target"` but can be edited to any label you prefer.

![Shortcuts tab](../assets/images/screenshots/shortcuts_tab.png)

## Executing a shortcut

When you run a shortcut, all settings from the **From** service are copied into the **To** service, overwriting its existing values. You can trigger a shortcut in two ways:

- From the **toolbar button** — click the dropdown arrow next to the plugin icon.
- From the **Database** menu → **PG service parser** submenu.

If either the source or target service no longer exists in your `pg_service.conf`, the shortcut action will be disabled.

## Removing a shortcut

Select a shortcut row and click the **−** button. A confirmation dialog will appear before deletion.
