# -*- coding:utf-8 -*-
# /usr/bin/python3
# this script will load first when program has started

def rd(filepath:str,encoding='utf-8')->str:
    with open(filepath,"r",encoding=encoding) as f:
        return f.read()

FATHER_ = "baseWIN"
FACE_ = "face"

loading = [
    ('./.fixed/transbk.qss','transbk_father'),
    ('./.fixed/face.qss','face_attr')
]

for path,key in loading:
    exec(f"{key}=rd('{path}')")