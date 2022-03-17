
# Русский военный корабль, иди нахуй

1. Create image embeddings in `.pt` format and locate it in `weigths` folder.

2. Create venv

```console
python3.8 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install git+https://github.com/openai/CLIP.git

In venv (either in jupyter or in python directly) run:

import clip
device = "cpu"
clip.load("ViT-B/32", device=device)

This will download ViT in cache.
```

3. Create model archive
`torch-model-archiver -f --model-name model1 --version 1.0  --serialized-file weights/img_feature.pt --handler model_handler.py --export-path model_store`

4. Serve model
`torchserve --start --model-store model_store --models model1.mar --ncs`

5. Test request
`curl http://127.0.0.1:8080/predictions/model1 -F "text=destroyed tank"`
