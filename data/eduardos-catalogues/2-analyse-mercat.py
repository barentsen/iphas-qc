"""This script runs through CASU's *.mercat catalogues and produces a CSV file
containing the summary info for all catalogues (one row per IPHAS field/run)"""

import os
import pyfits
import logging
import numpy as np
logging.basicConfig(level=logging.INFO)

merdir = "/home/gb/tmp/iphas_sep2012_eglez/apm3.ast.cam.ac.uk/~eglez/iphas/newmerges/"

csv = open("mercat-info.csv", "w")
csv.write("mercat,field,dir,run_r,run_i,run_ha,time" \
            + ",n_stars_r,n_stars_i,n_stars_ha,n_stars"\
            + ",n_bright_r,n_bright_i,n_bright_ha"\
            + ",n_stars_faint,r90p" \
            + ",zpr,zpi,zph,e_zpr,e_zpi,e_zpha" \
            + ",fluxr_5sig,fluxi_5sig,fluxha_5sig,exp_r,exp_i,exp_ha" \
            + ",ext_r,ext_i,ext_ha,air_r,air_i,air_ha\n")

csv_errors = open("corrupt-mercats.csv", "w")


# Function to flag and save info on *.mer files which seem corrupt!
def flag_problem(filename, message):
    logging.warning("%s : %s" % (filename, message))
    csv_errors.write("%s,%s\n" % (filename, message))
    csv_errors.flush()



for mydir in os.walk(merdir):
    for filename in mydir[2]:
        logging.info("%s/%s" % (mydir[0],filename))
        full_filename = os.path.join(mydir[0], filename)

        # Only consider files of the form intphas_xxxxx.mer
        if (not filename.startswith("intphas_")) or (not filename.endswith("_mercat.fits")):
                continue
        
        # Get dir and field number from filename
        rundir = full_filename.split("/")[-2]
        field = full_filename.split("/")[-1].split("_")[1]

        # Open file and header
        p = pyfits.open(full_filename)
        h = p[1].header

        # Check if the file is valid
        if len(p) != 5:
            flag_problem(full_filename, "NO_FIVE_EXTENSIONS")
            continue
        # Note: keyword FILTCOM1 is missing from Eduardo's files
        if not ( h.has_key("FILTREF") and h.has_key("FILTCOM2") \
            and h["FILTREF"] == "r" and h["FILTCOM2"] == "Halpha" ):
            flag_problem(full_filename, "INCORRECT_FILTER_COMPARISON")
            continue

        # Run numbers
        run_r = h['REFFILE'].split("r")[1].split("_")[0]
        run_i = h['COMFILE1'].split("r")[1].split("_")[0]
        run_ha = h['COMFILE2'].split("r")[1].split("_")[0]

        # Date/time of run_r
        try:
            time = h['DATEREF']+"T"+h['UTSTREF']
        except TypeError:
            time = ""

        # Count objects classified as strictly stellar (-1)
        n_stars_r, n_stars_i, n_stars_ha, n_stars = 0, 0, 0, 0
        n_stars_faint = 0
        r_mags = np.array([])
        for i in [1,2,3,4]:
            c_r = (p[i].data.field("rClass") == -1)
            c_i = (p[i].data.field("iClass") == -1)
            c_ha = (p[i].data.field("hClass") == -1)
            c_star = (c_r & c_i & c_ha)
            #rmag = h['MAGZPTR'] - 2.5*log10(p[i].data.field("Ref_core_fluxap")/h['EXPREF']) - (h['AIRMASR']-1.0)*h['EXTINCR']
            #c = logical_and( logical_and(rmag > 13.0, rmag < 19.0), p[i].data.field("Ref_class") == -1)
            n_stars_r += len(c_r[c_r])
            n_stars_i += len(c_i[c_i])
            n_stars_ha += len(c_ha[c_ha])
            n_stars += len(c_r[c_star])
            # Fetch the r magnitudes
            my_r_mags = p[i].data.field('rApermag3')[c_star]
            # Count the number of stars fainter than 21
            n_stars_faint += len( my_r_mags[my_r_mags > 19.5] )
            # Keep r magnitudes to compute the percentile below
            r_mags = np.concatenate((r_mags, my_r_mags))

            # Number of bright stars - useful for checking for double images
            n_bright_r = (p[i].data.field('rApermag3')[c_r] < 16).sum()
            n_bright_i = (p[i].data.field('iApermag3')[c_i] < 15).sum()
            n_bright_ha = (p[i].data.field('hApermag3')[c_ha] < 16).sum()
            

        
        # Compute the 90%-percentile of the r magnitude of stars
        if len(r_mags) > 0:
            r90p = np.percentile(r_mags, [90])[0]
        else:
            r90p = 0.0

        # Add a row for this field to the CSV file
        # NOTE: field h['EXTINCR'] is missing from Eduardo's files
        csv.write( ("%s,%s,%s,%s,%s,%s,%s," \
                    + "%s,%s,%s,%s," \
                    + "%s,%s,%s," \
                    + "%s,%.3f," \
                    + "%s,%s,%s,%s,%s,%s," \
                    + "%s,%s,%s,%s,%s,%s," \
                    + "%s,%s,%s,%s,%s,%s\n") % \
                    (full_filename.partition("eglez/iphas/")[2], \
                    field, rundir, run_r, run_i, run_ha, time, \
                    n_stars_r, n_stars_i, n_stars_ha, n_stars, \
                    n_bright_r, n_bright_i, n_bright_ha, \
                    n_stars_faint, r90p, \
                    h['MAGZPTR'], h['MAGZPTC1'], h['MAGZPTC2'], \
                    h['MAGZRRR'], h['MAGZRRC1'], h['MAGZRRC2'], \
                    h['FLIMREF'], h['FLIMCOM1'], h['FLIMCOM2'], \
                    h['EXPREF'], h['EXPCOM1'], h['EXPCOM2'], \
                    "", h['EXTINCC1'], h['EXTINCC2'], \
                    h['AIRMASR'], h['AIRMASC1'], h['AIRMASC2']) )
 
        csv.flush() # Sync CSV file to disk
        p.close() # Close FITS
        

# Important: sync CSV files to disk
csv.close()
csv_errors.close()
