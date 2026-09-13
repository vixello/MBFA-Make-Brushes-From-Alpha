## MBFA - Make Brush Froom Alpha Blender Addon ![Blender](https://img.shields.io/badge/-Blender-333333?style=flat&logo=blender) 


MBFA is a Blender addon that converts alpha images into reusable Blender brushes.

It supports both **Sculpt** and **Texture Paint** brushes and stores the generated brushes in a separate `Brushes.blend` asset library.


---

## Features

- Convert alpha images into Blender brushes
- Create **Sculpt** brushes
- Create **Texture Paint** brushes
- Browse alpha images inside Blender
- Preview alpha images
- Set individual brush names
- Configure brush settings
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

<img width="314" height="306" alt="obraz" src="https://github.com/user-attachments/assets/e0da684f-c8b3-4731-8b68-bc9f6b37108c" />

Click:

**Reload Alpha Folder**

MBFA will scan the folder and display all supported alpha images in the Alpha Browser.

---

## 2. Select Brush Type

Each alpha has a checkbox in the Alpha Browser.

| Checkbox | Brush Type |
|----------|------------|
| Unchecked | Sculpt |
| Checked | Texture Paint |

<img width="318" height="273" alt="obraz" src="https://github.com/user-attachments/assets/b7d69b44-76d0-4e06-9f9a-e3eda5df1ace" />

You can also change all alpha images at once using:

- **All Texture Paint**
- **All Sculpt**

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

After configuring your alpha images, click: `Add Brushes Function`

<img width="316" height="57" alt="obraz" src="https://github.com/user-attachments/assets/4a66cd11-a206-4d0c-919c-5ab1df63f1db" />

MBFA will generate the brushes and store them in the configured asset library.

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


