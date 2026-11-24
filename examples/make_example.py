"""Create an original synthetic line-art fixture; no external figure input."""
from pathlib import Path
import sys
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from pixel_theme import adapt

def main():
    folder=Path(__file__).resolve().parent
    src=folder/'synthetic_original.png';out=folder/'synthetic_dark.png'
    if src.exists() or out.exists():raise SystemExit('Example exists; keep the recorded copy or use a clean checkout')
    im=Image.new('RGB',(640,420),'white');d=ImageDraw.Draw(im);font=ImageFont.load_default(size=20)
    d.text((26,22),'Synthetic line art: not experimental data',fill='black',font=font)
    d.line((60,330,580,330),fill='black',width=2);d.line((60,330,60,90),fill='black',width=2)
    for i,(x,y,color) in enumerate([(120,265,'#56b4e9'),(230,195,'#ffcb3b'),(340,220,'#ef4797'),(450,140,'#48c97d')]):
        d.line((x,y-25,x,y+25),fill='black',width=2);d.line((x-8,y-25,x+8,y-25),fill='black',width=2);d.line((x-8,y+25,x+8,y+25),fill='black',width=2)
        d.ellipse((x-8,y-8,x+8,y+8),fill=color);d.text((x-12,347),chr(65+i),fill='black',font=font)
    d.text((400,80),'- 1.0',fill='black',font=font)
    d.line((500,195,560,195),fill='black',width=2);d.polygon([(560,195),(550,190),(550,200)],fill='black')
    d.text((26,385),'Inspect labels, error bars, arrows and colors.',fill='black',font=font)
    im.save(src)
    adapt(src,out,kind='line-art',mode='neutral-invert',tolerance=0,protect=[],mapping={})

if __name__=='__main__':main()
