# k9do-BSLRec
k9do-BSLRec aims to implement BSL (British Sign Language) into Pepper. Pepper will then perform a series of action based on recognized signs.

## Remark (Dev)
- The `process.py` should be working as is, awaiting implementation on ML BSL recognition. This is where the video feed from Pepper is received and processed with the BSL model. Outputs a character when sign is recognized and sent to `pepper_control.py`.
- `pepper_control.py` functions are to be done. Responsible for sending video feed and performing actions based on input from `process.py`.

## Requirements
**Python 3** packages required:
- opencv2
- numpy

**Python 2.7** packages required:
- Numpy (1.16.6)
- naoqi
> To install the naoqi package, please go to the official website for the [installation guide](https://www.bx.psu.edu/~thanh/naoqi/dev/python/install_guide.html)

***Installing Packages:***

```bash
#python2
python2 -m pip install numpy==1.16.6

#python3
python3 -m pip install numpy opencv-python
```

## Usage
Both `process.py` and `pepper_control.py` requires different python versions in order to work. Virtual environments could be setup to run them seperately but the following is also fine.

```bash
#Run this first
python2 pepper_control.py

#then this
python3 process.py

```

## Resources
- [Documentation](http://doc.aldebaran.com/2-1/naoqi/index.html) on how to use naoqi api
- A detailed video on how to program Pepper and port code from Choregraphe can be found [here](https://www.youtube.com/watch?v=iAeis7j5LmE).