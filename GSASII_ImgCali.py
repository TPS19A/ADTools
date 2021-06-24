import sys
if 'GSASIIscriptable' not in sys.modules.keys():
    if '/blsw/19a/software/GSASII' not in sys.path:
        sys.path.insert(0, '/blsw/19a/software/GSASII')
    import GSASIIscriptable as G2sc
if 'numpy' not in sys.modules.keys():
    import numpy as np

def ImgCali(img=None, gpxname=None, updateImgVals=None):
    # without GSASII img, open gpx and get img.
    if gpxname is not None:
        gpx = G2sc.G2Project(str(gpxname))
        num_Img = len(gpx.images())
        idx_slt = [gpx.image(i).getControl('dark image')[0] is not '' for i in range(num_Img)]
        idx_caliImg = (np.arange(num_Img)[idx_slt])[0]
        img = gpx.image(idx_caliImg)

    # initial image parameter settings
    updateImgVals = updateImgVals or {'center'    : [204.,163.],
                                      'wavelength': 0.61992, 
                                      'distance'  : 290.0,
                                      'tile'      : 0.0, 
                                      'phi'       : 285.0, 
                                      'DetDepth'  : 0.0, 
                                      'pixLimit'  : 10,  
                                      'cutoff'    : 2.0, 
                                      'calibdmin' : 0.85,}
    
    # set controls and vary options, then initial fit
    img.setCalibrant('LaB6  SRM660c')
    img.setVary('*',False)
    img.setVary(['det-X', 'det-Y', 'dist', 'tilt', 'phi'], True)
    img.setControls(updateImgVals)

    # start image recalibration
    pixRange = [10,5,3,2]
    for ni in pixRange:
        img.setControl('pixLimit',ni)
        print(f' === set pixel search range = {ni} ===')
        img.Recalibrate()
        chisq_old, chisq_new = 0, img.getControl('chisq')
        chisq_diff = np.round(abs(chisq_old - chisq_new), 4)
        recalc = int(0)
        while chisq_diff > 0.1:
            img.Recalibrate()
            chisq_old = chisq_new.copy()
            chisq_new = img.getControl('chisq')
            chisq_diff = np.round(abs(chisq_old - chisq_new), 4)
            print(f' === chisq diff = {chisq_diff} ===')
            recalc += 1
            if recalc > 3:
                break

    # save gpx
    if gpxname is not None:    
        #img.saveControls('test_img_cali.imctrl')
        gpx.save()
        
    return(img)






