import { contextIsolated, platform } from "node:process";
import { contextBridge, ipcRenderer, webFrame, webUtils } from "electron";
//#region ../../node_modules/.pnpm/@electron-toolkit+preload@3.0.2_electron@40.8.5/node_modules/@electron-toolkit/preload/dist/index.mjs
var electronAPI = {
	ipcRenderer: {
		send(channel, ...args) {
			ipcRenderer.send(channel, ...args);
		},
		sendTo(webContentsId, channel, ...args) {
			const electronVer = process.versions.electron;
			if ((electronVer ? parseInt(electronVer.split(".")[0]) : 0) >= 28) throw new Error("\"sendTo\" method has been removed since Electron 28.");
			else ipcRenderer.sendTo(webContentsId, channel, ...args);
		},
		sendSync(channel, ...args) {
			return ipcRenderer.sendSync(channel, ...args);
		},
		sendToHost(channel, ...args) {
			ipcRenderer.sendToHost(channel, ...args);
		},
		postMessage(channel, message, transfer) {
			ipcRenderer.postMessage(channel, message, transfer);
		},
		invoke(channel, ...args) {
			return ipcRenderer.invoke(channel, ...args);
		},
		on(channel, listener) {
			ipcRenderer.on(channel, listener);
			return () => {
				ipcRenderer.removeListener(channel, listener);
			};
		},
		once(channel, listener) {
			ipcRenderer.once(channel, listener);
			return () => {
				ipcRenderer.removeListener(channel, listener);
			};
		},
		removeListener(channel, listener) {
			ipcRenderer.removeListener(channel, listener);
			return this;
		},
		removeAllListeners(channel) {
			ipcRenderer.removeAllListeners(channel);
		}
	},
	webFrame: {
		insertCSS(css) {
			return webFrame.insertCSS(css);
		},
		setZoomFactor(factor) {
			if (typeof factor === "number" && factor > 0) webFrame.setZoomFactor(factor);
		},
		setZoomLevel(level) {
			if (typeof level === "number") webFrame.setZoomLevel(level);
		}
	},
	webUtils: { getPathForFile(file) {
		return webUtils.getPathForFile(file);
	} },
	process: {
		get platform() {
			return process.platform;
		},
		get versions() {
			return process.versions;
		},
		get env() {
			return { ...process.env };
		}
	}
};
//#endregion
//#region src/preload/shared.ts
function expose() {
	ipcRenderer.setMaxListeners(0);
	if (contextIsolated) try {
		contextBridge.exposeInMainWorld("electron", electronAPI);
		contextBridge.exposeInMainWorld("platform", platform);
	} catch (error) {
		console.error(error);
	}
	else {
		window.electron = electronAPI;
		window.platform = platform;
	}
}
//#endregion
export { expose as t };
