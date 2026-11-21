
# Jupyter Notebook: Kernel not found

After I uninstalled docling, the uninstallation process updated or cleaned up shared environment dependencies. Specifically, it left your Python environment with an updated version of setuptools (version 81.0.0 or higher), while leaving behind some legacy components of Jupyter or debugpy (Jupyter's background debugger) that still rely on the old declare_namespace function.

```bash
pip install "setuptools<81"
```
If this doesn't work then the cleanest, long-term solution is to update your local Jupyter installation and its underlying packages so they use modern, supported Python APIs.

```bash
pip install --upgrade --upgrade-strategy eager jupyter notebook ipykernel
```

