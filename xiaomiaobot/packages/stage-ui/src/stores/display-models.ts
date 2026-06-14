import localforage from 'localforage'

import { until } from '@vueuse/core'
import { nanoid } from 'nanoid'
import { defineStore } from 'pinia'
import { ref } from 'vue'

export enum DisplayModelFormat {
  Live2dZip = 'live2d-zip',
  Live2dDirectory = 'live2d-directory',
  VRM = 'vrm',
  PMXZip = 'pmx-zip',
  PMXDirectory = 'pmx-directory',
  PMD = 'pmd',
}

export type DisplayModel
  = | DisplayModelFile
    | DisplayModelURL

const presetLive2dProUrl = new URL('../assets/live2d/models/hiyori_pro_zh.zip', import.meta.url).href
const presetLive2dFreeUrl = new URL('../assets/live2d/models/hiyori_free_zh.zip', import.meta.url).href
const presetLive2dPreview = new URL('../assets/live2d/models/hiyori/preview.png', import.meta.url).href

// Cubism SDK sample models
const presetMarkUrl = new URL('../assets/live2d/models/mark.zip', import.meta.url).href
const presetMarkPreview = new URL('../assets/live2d/models/mark/preview.png', import.meta.url).href
const presetWankoUrl = new URL('../assets/live2d/models/wanko.zip', import.meta.url).href
const presetWankoPreview = new URL('../assets/live2d/models/wanko/preview.png', import.meta.url).href
const presetRiceUrl = new URL('../assets/live2d/models/rice.zip', import.meta.url).href
const presetRicePreview = new URL('../assets/live2d/models/rice/preview.png', import.meta.url).href
const presetNatoriUrl = new URL('../assets/live2d/models/natori.zip', import.meta.url).href
const presetNatoriPreview = new URL('../assets/live2d/models/natori/preview.png', import.meta.url).href
const presetHaruUrl = new URL('../assets/live2d/models/haru.zip', import.meta.url).href
const presetHaruPreview = new URL('../assets/live2d/models/haru/preview.png', import.meta.url).href
const presetMaoUrl = new URL('../assets/live2d/models/mao.zip', import.meta.url).href
const presetMaoPreview = new URL('../assets/live2d/models/mao/preview.png', import.meta.url).href

// Custom large models (not in git, users need to build locally)
const presetAtriUrl = new URL('../assets/live2d/models/atri.zip', import.meta.url).href
const presetAtriPreview = new URL('../assets/live2d/models/atri/preview.png', import.meta.url).href
const presetNatsumeUrl = new URL('../assets/live2d/models/natsume.zip', import.meta.url).href
const presetNatsumePreview = new URL('../assets/live2d/models/natsume/preview.png', import.meta.url).href

// VRM models
const presetVrmAvatarAUrl = new URL('../assets/vrm/models/AvatarSample-A/AvatarSample_A.vrm', import.meta.url).href
const presetVrmAvatarAPreview = new URL('../assets/vrm/models/AvatarSample-A/preview.png', import.meta.url).href
const presetVrmAvatarBUrl = new URL('../assets/vrm/models/AvatarSample-B/AvatarSample_B.vrm', import.meta.url).href
const presetVrmAvatarBPreview = new URL('../assets/vrm/models/AvatarSample-B/preview.png', import.meta.url).href

export interface DisplayModelFile {
  id: string
  format: DisplayModelFormat
  type: 'file'
  file: File
  name: string
  previewImage?: string
  importedAt: number
}

export interface DisplayModelURL {
  id: string
  format: DisplayModelFormat
  type: 'url'
  url: string
  name: string
  previewImage?: string
  importedAt: number
}

const displayModelsPresets: DisplayModel[] = [
  // Live2D models
  { id: 'preset-live2d-1', format: DisplayModelFormat.Live2dZip, type: 'url', url: presetLive2dProUrl, name: 'Hiyori (Pro)', previewImage: presetLive2dPreview, importedAt: 1733113886840 },
  { id: 'preset-live2d-2', format: DisplayModelFormat.Live2dZip, type: 'url', url: presetLive2dFreeUrl, name: 'Hiyori (Free)', previewImage: presetLive2dPreview, importedAt: 1733113886840 },
  { id: 'preset-live2d-3', format: DisplayModelFormat.Live2dZip, type: 'url', url: presetHaruUrl, name: 'Haru', previewImage: presetHaruPreview, importedAt: 1733113886841 },
  { id: 'preset-live2d-4', format: DisplayModelFormat.Live2dZip, type: 'url', url: presetMaoUrl, name: 'Mao', previewImage: presetMaoPreview, importedAt: 1733113886842 },
  { id: 'preset-live2d-5', format: DisplayModelFormat.Live2dZip, type: 'url', url: presetRiceUrl, name: 'Rice', previewImage: presetRicePreview, importedAt: 1733113886843 },
  { id: 'preset-live2d-6', format: DisplayModelFormat.Live2dZip, type: 'url', url: presetNatoriUrl, name: 'Natori', previewImage: presetNatoriPreview, importedAt: 1733113886844 },
  { id: 'preset-live2d-7', format: DisplayModelFormat.Live2dZip, type: 'url', url: presetMarkUrl, name: 'Mark', previewImage: presetMarkPreview, importedAt: 1733113886845 },
  { id: 'preset-live2d-8', format: DisplayModelFormat.Live2dZip, type: 'url', url: presetWankoUrl, name: 'Wanko', previewImage: presetWankoPreview, importedAt: 1733113886846 },
  // NOTE: ATRI (588MB) and Natsume (84MB) are commented out due to large file size
  // causing slow page load. Users can add them manually via the "Add" button.
  // Uncomment these lines if you want them in the preset list:
  // { id: 'preset-live2d-9', format: DisplayModelFormat.Live2dZip, type: 'url', url: presetAtriUrl, name: 'ATRI', previewImage: presetAtriPreview, importedAt: 1733113886847 },
  // { id: 'preset-live2d-10', format: DisplayModelFormat.Live2dZip, type: 'url', url: presetNatsumeUrl, name: 'Natsume', previewImage: presetNatsumePreview, importedAt: 1733113886848 },

  // VRM models
  { id: 'preset-vrm-1', format: DisplayModelFormat.VRM, type: 'url', url: presetVrmAvatarAUrl, name: 'AvatarSample_A', previewImage: presetVrmAvatarAPreview, importedAt: 1733113886840 },
  { id: 'preset-vrm-2', format: DisplayModelFormat.VRM, type: 'url', url: presetVrmAvatarBUrl, name: 'AvatarSample_B', previewImage: presetVrmAvatarBPreview, importedAt: 1733113886840 },
]

export const useDisplayModelsStore = defineStore('display-models', () => {
  const displayModels = ref<DisplayModel[]>([])

  let generateLive2DPreview: (file: File) => Promise<string | undefined>
  let generateVrmPreview: (file: File) => Promise<string | undefined>

  const displayModelsFromIndexedDBLoading = ref(false)

  async function loadDisplayModelsFromIndexedDB() {
    await until(displayModelsFromIndexedDBLoading).toBe(false)

    displayModelsFromIndexedDBLoading.value = true
    const models = [...displayModelsPresets]

    try {
      await localforage.iterate<{ format: DisplayModelFormat, file: File, importedAt: number, previewImage?: string }, void>((val, key) => {
        if (key.startsWith('display-model-')) {
          models.push({ id: key, format: val.format, type: 'file', file: val.file, name: val.file.name, importedAt: val.importedAt, previewImage: val.previewImage })
        }
      })
    }
    catch (err) {
      console.error(err)
    }

    displayModels.value = models.sort((a, b) => b.importedAt - a.importedAt)
    displayModelsFromIndexedDBLoading.value = false
  }

  async function getDisplayModel(id: string) {
    await until(displayModelsFromIndexedDBLoading).toBe(false)
    const modelFromFile = await localforage.getItem<DisplayModelFile>(id)
    if (modelFromFile) {
      return modelFromFile
    }

    // Fallback to in-memory presets if not found in localforage
    return displayModelsPresets.find(model => model.id === id)
  }

  const loadLive2DModelPreview = (file: File) => generateLive2DPreview(file)
  const loadVrmModelPreview = (file: File) => generateVrmPreview(file)

  async function addDisplayModel(format: DisplayModelFormat, file: File) {
    await until(displayModelsFromIndexedDBLoading).toBe(false)
    const newDisplayModel: DisplayModelFile = { id: `display-model-${nanoid()}`, format, type: 'file', file, name: file.name, importedAt: Date.now() }

    if (format === DisplayModelFormat.Live2dZip) {
      const previewImage = await loadLive2DModelPreview(file)
      newDisplayModel.previewImage = previewImage
    }
    else if (format === DisplayModelFormat.VRM) {
      const previewImage = await loadVrmModelPreview(file)
      newDisplayModel.previewImage = previewImage
    }

    displayModels.value.unshift(newDisplayModel)

    localforage.setItem<DisplayModelFile>(newDisplayModel.id, newDisplayModel)
      .catch(err => console.error(err))
  }

  async function renameDisplayModel(id: string, name: string) {
    await until(displayModelsFromIndexedDBLoading).toBe(false)
    const displayModel = await localforage.getItem<DisplayModelFile>(id)
    if (!displayModel)
      return

    displayModel.name = name
  }

  async function removeDisplayModel(id: string) {
    await until(displayModelsFromIndexedDBLoading).toBe(false)
    await localforage.removeItem(id)
    displayModels.value = displayModels.value.filter(model => model.id !== id)
  }

  async function resetDisplayModels() {
    await loadDisplayModelsFromIndexedDB()
    const userModelIds = displayModels.value.filter(model => model.type === 'file').map(model => model.id)
    for (const id of userModelIds) {
      await removeDisplayModel(id)
    }

    displayModels.value = [...displayModelsPresets].sort((a, b) => b.importedAt - a.importedAt)
  }

  async function initialize() {
    await import('@proj-airi/stage-ui-live2d/utils/live2d-zip-loader')
    await import('@proj-airi/stage-ui-live2d/utils/live2d-opfs-registration')

    const { loadLive2DModelPreview } = await import('@proj-airi/stage-ui-live2d/utils/live2d-preview')
    const { loadVrmModelPreview } = await import('@proj-airi/stage-ui-three/utils/vrm-preview')

    generateLive2DPreview = loadLive2DModelPreview
    generateVrmPreview = loadVrmModelPreview
  }

  return {
    displayModels,
    displayModelsFromIndexedDBLoading,

    initialize,
    loadDisplayModelsFromIndexedDB,
    getDisplayModel,
    addDisplayModel,
    renameDisplayModel,
    removeDisplayModel,
    resetDisplayModels,
  }
})
