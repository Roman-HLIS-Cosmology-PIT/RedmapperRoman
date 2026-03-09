import numpy as np
import healpy as hp
import fitsio, esutil
import os, h5py, joblib

class RomanCollator:
    
    def __init__(self, outBase, bands = ['F106', 'F129', 'F158', 'F184'], nside = 8, n_jobs = -1):
        self.outBase = outBase
        self.nside   = nside
        self.n_jobs  = n_jobs


        self.bands   = bands

        self.dtypeBasic = [('ra', 'f8'),
                           ('dec', 'f8')]
        
        self.dtypeBDF = ([(f'flux_{b}', 'f4') for b in self.bands] + 
                         [(f'fluxerr_{b}', 'f4') for b in self.bands])


    def run(self, inputfile):

        with h5py.File(inputfile, 'r') as inCat:
            ipring = hp.ang2pix(self.nside, inCat['ra'][:], inCat['dec'][:], lonlat=True)

        pixMin = ipring.min()
        pixMax = ipring.max()

        h, rev = esutil.stat.histogram(ipring, rev=True, min=pixMin, max=pixMax)
        hpix   = np.arange(pixMin, pixMax+1, dtype='i8')

        np.save(self.outBase + '.tmp_rev.npy',  rev)
        np.save(self.outBase + '.tmp_h.npy',    h)
        np.save(self.outBase + '.tmp_hpix.npy', hpix)

        jobs = [joblib.delayed(self._single_step)(inputfile, i) for i in range(hpix.size)]
        out  = joblib.Parallel(n_jobs = self.n_jobs, verbose = 10)(jobs)

        assert np.sum(out) == ipring.size, f"Input catalog has size {ipring.size} but only wrote {np.sum(out)} files to FITS"

        os.remove(self.outBase + '.tmp_h.npy')
        os.remove(self.outBase + '.tmp_hpix.npy')
        os.remove(self.outBase + '.tmp_rev.npy')

    def _single_step(self, inputfile, i, verbose = False):

        h    = np.load(self.outBase + '.tmp_h.npy',    mmap_mode = 'r')
        hpix = np.load(self.outBase + '.tmp_hpix.npy', mmap_mode = 'r')
        rev  = np.load(self.outBase + '.tmp_rev.npy',  mmap_mode = 'r')

        if (h[i] == 0): return 0

        i1a = rev[rev[i]:rev[i+1]]
        start = i1a.min()
        end   = i1a.max() + 1 #Plus 1 is needed since end-index is not inclusive in python slicing
        sub   = slice(start, end)
        imod  = i1a - start 

        basicCat = np.zeros(i1a.size, dtype = self.dtypeBasic)

        with h5py.File(inputfile, 'r') as inCat:
            basicCat['ra']  = inCat['ra'][sub][:][imod]
            basicCat['dec'] = inCat['dec'][sub][:][imod]

            bdfCat = np.zeros(i1a.size, dtype = self.dtypeBDF)
            if verbose: print(i, "band started", flush=True)

            for b in self.bands:
                bdfCat['flux_' + b]    = inCat['flux_' + b][sub][:][imod]
                bdfCat['fluxerr_' + b] = inCat['fluxerr_' + b][sub][:][imod]
                
                if verbose: print(i,"band ", b, " done", flush=True)

        basicFile = '%s_pix%05d_basic.fits' % (self.outBase, hpix[i])
        bdfFile   = '%s_pix%05d_flux.fits'   % (self.outBase, hpix[i])

        fitsio.write(basicFile, basicCat, clobber=True)
        fitsio.write(bdfFile,   bdfCat,   clobber=True)
        if verbose: print(i, "Done", flush=True)

        return len(bdfCat)