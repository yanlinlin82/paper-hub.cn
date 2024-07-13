rsvg-convert -a -w 256 -h 256 paper-hub-logo.40x40.svg -o paper-hub-logo.256x256.png
convert paper-hub-logo.256x256.png -define icon:auto-resize=256,128,64,48,32,16 paper-hub.ico

rsvg-convert -a -w 300 -h 80 paper-hub-banner.150x40-white-text.svg -o paper-hub-banner.300x80-white-text.png
rsvg-convert -a -w 300 -h 80  paper-hub-banner.150x40-black-text.svg -o paper-hub-banner.300x80-black-text.png

cp -av paper-hub-banner.300x80-white-text.png ../static/images/banner-w.png
cp -av paper-hub.ico ../static/favicon.ico
