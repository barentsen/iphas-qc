"""This script runs through CASU's *.mer catalogues and produces a CSV file
containing the summary info for all catalogues (one row per IPHAS field/run)"""

import os
import pyfits
import logging
logging.basicConfig(level=logging.INFO)

merdir = "/home/gb/ext/surveys/iphas/iphas_aug2012_mike/apm3.ast.cam.ac.uk/~mike/iphas/"

csv = open("mer-info.csv", "w")
csv.write("field,dir,run_r,run_i,run_ha,time" \
            + ",n_stars_r,n_stars_i,n_stars_ha,n_stars"\
            + ",zpr,zpi,zph,e_zpr,e_zpi,e_zpha" \
            + ",fluxr_5sig,fluxi_5sig,fluxha_5sig,exp_r,exp_i,exp_ha" \
            + ",ext_r,ext_i,ext_ha,air_r,air_i,air_ha\n")

csv_errors = open("corrupt-mers.csv", "w")


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
        if (not filename.startswith("intphas")) or (not filename.endswith(".mer")):
                continue
        
        # Get dir and field number from filename
        rundir = full_filename.split("/")[-3]
        field = full_filename.split("/")[-1].split("_")[1].split(".")[0]

        # Open file and header
        p = pyfits.open(full_filename)
        h = p[1].header

        # Check if the file is valid
        if len(p) != 5:
            flag_problem(full_filename, "NO_FIVE_EXTENSIONS")
            continue
        if not ( h.has_key("FILTREF") and h.has_key("FILTCOM1") and h.has_key("FILTCOM2") \
            and h["FILTREF"] == "r" and h["FILTCOM1"] == "i" and h["FILTCOM2"] == "Halpha" ):
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
        for i in [1,2,3,4]:
            c_r = (p[i].data.field("Ref_class") == -1)
            c_i = (p[i].data.field("Com1_class") == -1)
            c_ha = (p[i].data.field("Com2_class") == -1)
            #rmag = h['MAGZPTR'] - 2.5*log10(p[i].data.field("Ref_core_fluxap")/h['EXPREF']) - (h['AIRMASR']-1.0)*h['EXTINCR']
            #c = logical_and( logical_and(rmag > 13.0, rmag < 19.0), p[i].data.field("Ref_class") == -1)
            n_stars_r += len(c_r[c_r])
            n_stars_i += len(c_i[c_i])
            n_stars_ha += len(c_ha[c_ha])
            n_stars += len(c_r[c_r & c_i & c_ha])


        # Add a row for this field to the CSV file
        csv.write( ("%s,%s,%s,%s,%s,%s," \
                    + "%s,%s,%s,%s," \
                    + "%s,%s,%s,%s,%s,%s," \
                    + "%s,%s,%s,%s,%s,%s," \
                    + "%s,%s,%s,%s,%s,%s\n") % \
                    (field, rundir, run_r, run_i, run_ha, time, \
                    n_stars_r, n_stars_i, n_stars_ha, n_stars, \
                    h['MAGZPTR'], h['MAGZPTC1'], h['MAGZPTC2'], \
                    h['MAGZRRR'], h['MAGZRRC1'], h['MAGZRRC2'], \
                    h['FLIMREF'], h['FLIMCOM1'], h['FLIMCOM2'], \
                    h['EXPREF'], h['EXPCOM1'], h['EXPCOM2'], \
                    h['EXTINCR'], h['EXTINCC1'], h['EXTINCC2'], \
                    h['AIRMASR'], h['AIRMASC1'], h['AIRMASC2']) )
 
        csv.flush() # Sync CSV file to disk
        p.close() # Close FITS
        

# Important: sync CSV files to disk
csv.close()
csv_errors.close()
