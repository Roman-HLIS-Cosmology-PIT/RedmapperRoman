import fitsio, glob
import numpy as np, healpy as hp
import redmapper
import h5py
from astropy.table import Table


######################################################################################################
# 1. MAKE THE HDF5 CATALOG FOR INPUT
######################################################################################################

with h5py.File('/project/chihway/chto/Roman/combine_v3.h5', 'r') as cat:
    catselect = np.load('/project/chihway/chto/Roman/batchrun_new/Rd_select.npy',      mmap_mode='r')

    # choose the 100 deg^2 region
    ra           = np.array(cat['catalog/gold/ra'][:][catselect],  dtype='f8')
    dec          = np.array(cat['catalog/gold/dec'][:][catselect], dtype='f8')
    FilterRA     = np.logical_and(130.0 <= ra, ra <= 140.0)
    FilterDEC    = np.logical_and(20.0 <= dec, dec <= 30.0)
    FilterRegion = np.logical_and(FilterRA, FilterDEC)

    print("LOADED AND CUT")

    del FilterRA, FilterDEC
    FluxRoman    = np.load('/project/chihway/chto/Roman/batchrun_new/Rd_Roman.npy',    mmap_mode='r')[FilterRegion]
    FluxerrRoman = np.load('/project/chihway/chto/Roman/batchrun_new/Rd_Romanerr.npy', mmap_mode='r')[FilterRegion]
    FluxLSST     = np.load('/project/chihway/chto/Roman/batchrun_new/Rd_LSST.npy',     mmap_mode='r')[FilterRegion]
    FluxerrLSST  = np.load('/project/chihway/chto/Roman/batchrun_new/Rd_LSSTerr.npy',  mmap_mode='r')[FilterRegion]

    influx_err = np.concatenate((FluxerrLSST, FluxerrRoman), axis=1)
    influx =np.concatenate((FluxLSST, FluxRoman), axis=1)
    b_array = np.array([1.4e-12, 9.0e-13, 1.2e-12, 1.8e-12, 7.4e-12,7.4e-12,7.4e-12,7.4e-12,7.4e-12,7.4e-12])
    zp      = 22.5

    print("LOADED FLUXES")

    Filter    = np.load('/project/chihway/chto/Roman/FilterNegativeFluxLargeMag_err.npy', mmap_mode='r')[FilterRegion]

    galaxy_id = np.array(cat['catalog/gold/id'][:][catselect][FilterRegion],  dtype='i8')[Filter]
    ra        = np.array(cat['catalog/gold/ra'][:][catselect][FilterRegion],  dtype='f8')[Filter]
    dec       = np.array(cat['catalog/gold/dec'][:][catselect][FilterRegion], dtype='f8')[Filter]
    ztrue     = np.array(cat['catalog/gold/z'][:][catselect][FilterRegion],   dtype='f4')[Filter]
    M200      = np.array(cat['catalog/gold/M200'][:][catselect][FilterRegion],   dtype='f4')[Filter]
    Central   = np.array(cat['catalog/gold/central'][:][catselect][FilterRegion],   dtype='i2')[Filter]
    influx    = influx[Filter]
    influx_err= influx_err[Filter]


with h5py.File("/project/chihway/dhayaa/Roman/Cardinal/MockRun/RomanGold.hdf5", "w") as f:
    f.create_dataset("id",  data = galaxy_id)
    f.create_dataset("ra",  data = ra)
    f.create_dataset("dec", data = dec)

    for i,b in enumerate(['u', 'g', 'r', 'i', 'z', 'y', 'F106', 'F129', 'F158', 'F184']):
        f.create_dataset(f"flux_{b}", data=influx[:, i])
        f.create_dataset(f"fluxerr_{b}", data=influx_err[:, i])

    #Just save this for future reference
    f.attrs["zeropoint"] = zp
    f.attrs["b_array"]   = b_array



######################################################################################################
# 2. MAKE A SQUARE HPIX MASK TO PASS IN
######################################################################################################

def healpix_radec_rect_mask(nside, ra_min, ra_max, dec_min, dec_max, nest=False, dtype=np.uint8):
    """
    Return a HEALPix mask (size hp.nside2npix(nside)) that is 1 inside
    the RA/Dec rectangle and 0 elsewhere.

    Angles in degrees. RA assumed in [0, 360).
    Handles RA wrap-around (e.g. ra_min=350, ra_max=10).
    """
    npix = hp.nside2npix(nside)
    ipix = np.arange(npix)

    theta, phi = hp.pix2ang(nside, ipix, nest=nest)  # theta: colat [0,pi], phi: lon [0,2pi)
    ra = np.degrees(phi)                              # [0, 360)
    dec = 90.0 - np.degrees(theta)                    # [-90, 90]

    # Dec cut
    in_dec = (dec >= dec_min) & (dec <= dec_max)

    # RA cut (with wrap support)
    ra_min = ra_min % 360.0
    ra_max = ra_max % 360.0
    if ra_min <= ra_max:
        in_ra = (ra >= ra_min) & (ra <= ra_max)
    else:
        # wrap-around: e.g. [350, 360) U [0, 10]
        in_ra = (ra >= ra_min) | (ra <= ra_max)

    mask = np.zeros(npix, dtype=dtype)
    mask[in_ra & in_dec] = 1
    return mask


footprint_mask  = healpix_radec_rect_mask(4096, 130, 140, 20, 30, nest = False) #Sets where the survey observed data
foreground_mask = np.zeros_like(footprint_mask) #Should be 0 where data is good to use

hp.write_map("/project/chihway/dhayaa/Roman/Cardinal/MockRun/Masks/footprint_mask.hpy",  footprint_mask,  dtype = np.int16, overwrite = True)
hp.write_map("/project/chihway/dhayaa/Roman/Cardinal/MockRun/Masks/foreground_mask.hpy", foreground_mask, dtype = np.int16, overwrite = True)


#We need to mock up some survey property maps.
#For now, I have set these to just 1s, but later
#need to ask Chun-Hao for better ones (Roman sims probably)
bands = ['U', 'G', 'R', 'I', 'Z', 'F106', 'F129', 'F158', 'F184']
maps  = ['maglim', 'fwhm', 'airmass', 'exptime', 'skybrite']

INPUT = np.ones(12 * 4096**2)
for b in bands:
    for m in maps:
        path = "/project/chihway/dhayaa/Roman/Cardinal/MockRun/SPmaps/MAP_%s_%s.hpy" % (b, m)
        hp.write_map(path, INPUT)
        
        print("WRITTEN", b, m)



######################################################################################################
# 3. Now make a mock spectroscopic sample.

# This just takes the original gal catalog and
# subselects a few of them to serve as a spec-z
# sample.
######################################################################################################

# Read in the data
cat       = h5py.File('/project/chihway/chto/Roman/combine_v3.h5', 'r')
M200      = np.array(cat['catalog/gold/M200'][:],   dtype='f4')
Central   = np.array(cat['catalog/gold/central'][:],   dtype='i2')
catselect = np.where(np.load('/project/chihway/chto/Roman/batchrun_new/Rd_select.npy', mmap_mode='r'))[0]
selectnew = []
catselect = catselect[(Central[catselect]>0)&(M200[catselect]>5E13)]

# choose the 100 deg^2 region
ra           = np.array(cat['catalog/gold/ra'][:][catselect],  dtype='f8')
dec          = np.array(cat['catalog/gold/dec'][:][catselect], dtype='f8')
FilterRA     = np.logical_and(130.0 <= ra, ra <= 140.0)
FilterDEC    = np.logical_and(20.0 <= dec, dec <= 30.0)
FilterRegion = np.logical_and(FilterRA, FilterDEC)

z            = np.array(cat['catalog/gold/z'][:][catselect],  dtype='f8')
zmax         = 2.3
FilterZ      = np.logical_and(0.0 <= z, z <= zmax)
FilterAll    = np.logical_and(FilterRegion, FilterZ)

# Randomly select 2000 galaxies
redshiftbin=np.arange(0.0, zmax, 0.01)
RandomSample = []
nsample=500
for zmin, zmax in zip(redshiftbin[:-1], redshiftbin[1:]):
    mask = np.where(z[FilterAll])[0]
    np.random.shuffle(mask)
    RandomSample.append(mask[:nsample])
RandomSample = np.hstack(RandomSample)


ztrue     = np.array(cat['catalog/gold/z'][:][catselect][FilterAll][RandomSample],   dtype='f4')
ra        = np.array(cat['catalog/gold/ra'][:][catselect][FilterAll][RandomSample],  dtype='f8')
dec       = np.array(cat['catalog/gold/dec'][:][catselect][FilterAll][RandomSample], dtype='f8')
z_err     = np.ones(np.shape(dec)) * 0.00001


# Save the data
# No z_err
table = Table()
table['ra'] = ra
table['dec'] = dec
table['z'] = ztrue
table['z_err'] = z_err

table.write('/project/chihway/dhayaa/Roman/Cardinal/MockRun/SpeczSample.fits', format='fits', overwrite=True)