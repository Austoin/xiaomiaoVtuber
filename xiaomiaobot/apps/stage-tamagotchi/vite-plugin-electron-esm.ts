/**
 * Vite plugin to fix Electron ESM import issue in Node.js v24+.
 *
 * NOTICE:
 * Electron in Node.js v24 ESM mode does not work with any form of import.
 * This is a known Electron bug affecting all versions.
 *
 * Workaround: Use Node.js's createRequire to load electron as CommonJS module.
 *
 * This plugin transforms:
 *   import { app, BrowserWindow } from 'electron'
 * to:
 *   import { createRequire } from 'node:module';
 *   const __electron_require = createRequire(import.meta.url);
 *   const { app, BrowserWindow } = __electron_require('electron');
 *
 * This allows ESM code to load electron via CommonJS interop.
 */

import type { Plugin } from 'vite'

export function electronESMCompat(): Plugin {
  return {
    name: 'electron-esm-compat',

    generateBundle(options, bundle) {
      for (const fileName in bundle) {
        const chunk = bundle[fileName]

        // Only process JS chunk files (not assets)
        if (chunk.type === 'chunk' && fileName.endsWith('.js')) {
          // Match: import { ...exports } from 'electron' or "electron"
          const electronImportRegex = /import\s+\{[^}]+\}\s+from\s+['"]electron['"]/

          if (electronImportRegex.test(chunk.code)) {
            // Collect all electron imports
            const electronImports: string[] = []

            chunk.code = chunk.code.replace(
              /import\s+\{([^}]+)\}\s+from\s+['"]electron['"]/g,
              (match, exports) => {
                // Convert "Foo as Bar" to "Foo: Bar" for destructuring syntax
                const transformedExports = exports.replace(/\s+as\s+/g, ': ')
                electronImports.push(transformedExports)
                // Remove the import statement
                return ''
              },
            )

            // Add createRequire-based loading at the top
            if (electronImports.length > 0) {
              const allExports = electronImports.join(', ')
              chunk.code = `import { createRequire as __createRequire } from "node:module";\nconst __electron_require = __createRequire(import.meta.url);\nconst { ${allExports} } = __electron_require('electron');\n${chunk.code}`
            }
          }
        }
      }
    },
  }
}
