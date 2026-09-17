## MBFA - Make Brush From Alpha Blender Addon ![Blender](https://img.shields.io/badge/-Blender-333333?style=flat&logo=blender) 


MBFA is a Blender addon that converts alpha images into reusable Blender brushes.

It supports both **Sculpt** and **Texture Paint** brushes and stores the generated brushes in a separate `.blend` file of choice.


---

## Features

- Convert alpha images into Blender brushes
- Create **Sculpt** brushes
- Create **Texture Paint** brushes
- Browse alpha images inside Blender
- Preview alpha images
- Configure brush settings: `name`, `stroke method`, `size`, `strength`, `spacing`, `invert alpha`
- Batch set all brushes to Sculpt
- Batch set all brushes to Texture Paint
- Store brushes in a separate `.blend` file
- Preserve existing brushes in said `.blend` file
- Support multiple alpha image formats:
  - `.png`
  - `.jpg`
  - `.jpeg`
  - `.tif`
  - `.bmp`
  - `.psd`
- Asset Catalog management:
    - Create catalogs
    - Rename catalogs
    - Delete catalogs
    - Assign brushes to catalogs
    - Read catalog assignments from external .blend files
      
## Requirements

- Blender 5.2 or newer

---

## Installation

1. Download the MBFA addon.
2. Open Blender.
3. Go to:

   **Edit > Preferences > Add-ons**

4. Click **Install...**
5. Select the MBFA `.zip` file.
6. Enable **Make Brush From Alpha**.
7. Open the 3D Viewport sidebar by pressing `N`.
8. Select the **MBFA** tab.

---

# How To Use

## 1. Select an Alpha Folder

In the MBFA panel, select the folder containing your alpha images.

<img width="342" height="230" alt="obraz" src="https://github.com/user-attachments/assets/d369a8e7-e081-4071-8a03-f36bc94a3730" />

Click:

**Reload Alpha Folder**

MBFA will scan the folder and display all supported alpha images in the Alpha Browser.

---

## 2. Select Brush Type

Each alpha has a checkbox for selection (first to the left) and for marking it as sculpting or texture paint brush (second to the left) in the Alpha Browser.
<img width="62" height="32" alt="obraz" src="https://github.com/user-attachments/assets/c8deede4-56c7-4520-b05e-9fa5f9a20c00" />

| Checkbox 2 | Brush Type |
|----------|------------|
| Unchecked | Sculpt |
| Checked | Texture Paint |

<img width="337" height="304" alt="obraz" src="https://github.com/user-attachments/assets/50bc337f-60f3-4ca6-a564-309481aa4a9d" />

You can also change all alpha images at once using:

`All Texture Paint`
`All Sculpt`

Or `Select all` for assigning it to a catalog.

---

## 3. Configure the Brush

Select an alpha from the Alpha Browser.

You can configure:

- Brush Name
- Stroke Method
- Size
- Strength
- Spacing

<img width="315" height="475" alt="obraz" src="https://github.com/user-attachments/assets/77b6ab35-2f82-4909-bc13-e80eb5517279" />

## 🖌 Creating Brushes

After configuring your alpha images, click: `Add Brushes From Alpha`

<img width="316" height="57" alt="obraz" src="https://github.com/user-attachments/assets/4a66cd11-a206-4d0c-919c-5ab1df63f1db" />

MBFA will generate the brushes and store them in the configured asset library.

---

## Asset Catalogs

MBFA includes a built‑in Asset Catalog Manager that lets you organize generated brushes inside Blender’s Asset Browser. Catalogs help you group brushes (e.g., Skin, Hard Surface, Fabric, Stamps, Noise, etc.) and keep large brush libraries tidy.

The asset catalog browser UI:

<img width="335" height="218" alt="obraz" src="https://github.com/user-attachments/assets/4209f238-1320-4af9-aae9-d369c434ea18" />

To add a brush to the catalog, selecte it in the alpha browser list and click `Assing Selected` in the Asset Catalogs.

---

## 📁 Brushes Asset Library

MBFA uses a separate `.blend` file to store all generated brushes.

Example structure:
```
Brushes/
└── Brushes.blend
```

You can configure the location using:

`Brushes Asset Library `
`Brushes Blend File Name`


