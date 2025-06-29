git clone https://github.com/taesungp/contrastive-unpaired-translation
cd contrastive-unpaired-translation
uv pip install -r requirements.txt

make sure torch and numpy have right version:
uv pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
uv pip install numpy<2

if train_cut.sh crashes on windows, manually start visdom:
python -m visdom.server

folder structure:

-constrative-unpaired-translation
    -datasets
        -synth2real
            -trainA
            -trainB
            -testA
            -testB

testB images are required even without matching

num_threads > 0 might cause issues on windows