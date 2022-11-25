#!/bin/sh -xe

output=$1

if [ -z "$output" ]; then
    output="weather.png"
fi

dir="$(dirname "${output}")"

rawfile="${dir}/raw.$(basename ${output})"
rm -f ${rawfile}
python3 "${dir}/weather.py" > "${dir}/out.html"

# for whatever reason, if i use cutycapt file:///, i get some horrible webkit
# permissions error :(
xvfb-run --server-args="-screen 0, 640x480x24" cutycapt --url=https://tycho.pizza/dash/out.html --out=${rawfile}
convert \( "${rawfile}" -background white -extent 600x800 \) "${output}"
