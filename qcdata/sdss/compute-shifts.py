"""This script runs through CASU's *.mercat catalogues and produces a CSV file
containing the summary info for all catalogues (one row per IPHAS field/run)"""

import os
import pyfits
import numpy as np
import sys, logging
import db
mydb = db.db()


logging.basicConfig(level=logging.INFO, stream=sys.stdout)

merdir = "/home/gb/tmp/iphas_sep2012_eglez/apm3.ast.cam.ac.uk/~eglez/iphas/newmerges/"

csv = open("shifts.csv", "w")
csv.write("field,dir,run_r,run_i,run_ha," \
            + "sdss_stars,sdss_r,sdss_i,sdss_r_std,sdss_i_std," \
            + "apass_stars,apass_r,apass_i,apass_r_std,apass_i_std\n")

csv_errors = open("corrupt-mercats.csv", "w")

csv_sdss = open("iphas_x_sdss.csv", "w")
csv_sdss.write("field,dir,iphas_ra,iphas_dec,iphas_r,iphas_i,sdss_ra,sdss_dec,sdss_g,sdss_r,sdss_i\n")

csv_apass = open("iphas_x_apass.csv", "w")
csv_apass.write("field,dir,iphas_ra,iphas_dec,iphas_r,iphas_i,apass_ra,apass_dec,apass_g,apass_r,apass_i\n")


# Function to flag and save info on *.mer files which seem corrupt!
def flag_problem(filename, message):
    logging.warning("%s : %s" % (filename, message))
    csv_errors.write("%s,%s\n" % (filename, message))
    csv_errors.flush()




def prepare_ra_condition(ra1, ra2):
    # Be tolerant on input
    if ra1 > 360: ra1 -= 360
    if ra2 > 360: ra2 -= 360
    if ra1 < 0: ra1 += 360
    if ra2 < 0: ra2 += 360
    # Create the condition
    if (ra1 - ra2) > 180:
        rasql = "(ra > %.14f OR ra < %.14f)" % (ra1, ra2)
    elif (ra2 - ra1) > 180:
        rasql = "(ra > %.14f OR ra < %.14f)" % (ra2, ra1)
    elif ra1 > ra2:
        rasql = "ra BETWEEN %.14f AND %.14f" % (ra2, ra1)
    else:
        rasql = "ra BETWEEN %.14f AND %.14f" % (ra1, ra2)
    return rasql   

def get_sdss(ra1, ra2, dec1, dec2, sdss_condition=""):
    rasql = prepare_ra_condition(ra1, ra2)
    sql = """
        SELECT 
            ra, dec,
            g, r, i
        FROM     
            sdss_dr9
        WHERE
            %s
            AND dec BETWEEN %.14f AND %.14f 
            %s
    """ % (rasql, dec1, dec2, sdss_condition)
    logging.debug(sql)
    return mydb.sql(sql)


def get_apass(ra1, ra2, dec1, dec2, apass_condition=""):
    rasql = prepare_ra_condition(ra1, ra2)
    sql = """
        SELECT 
            ra, dec,
            g, r, i
        FROM     
            apass_dr6
        WHERE
            %s
            AND dec BETWEEN %.14f AND %.14f 
            %s
    """ % (rasql, dec1, dec2, apass_condition)
    logging.debug(sql)
    return mydb.sql(sql)    




######################
# LOOP OVER ALL FIELDS
######################
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

       
        
        # Count objects classified as strictly stellar (-1)
        n_stars_r, n_stars_i, n_stars_ha, n_stars = 0, 0, 0, 0
        iphas_ra, iphas_dec, iphas_r, iphas_i = np.array([]), [], [], []
        for i in [1,2,3,4]:
            # Select strictly stellar objects
            c_r = (p[i].data.field("rClass") == -1)
            c_r2 = (p[i].data.field("rApermag3") > 14) & (p[i].data.field("rApermag3") < 18)
            c_i = (p[i].data.field("iClass") == -1)
            c_i2 = (p[i].data.field("iApermag3") > 14) & (p[i].data.field("iApermag3") < 18.5)
            c = (c_r & c_r2 & c_i & c_i2)

            iphas_ra = np.concatenate( (iphas_ra, p[i].data.field("RA")[c]) )
            iphas_dec = np.concatenate(( iphas_dec, p[i].data.field("DEC")[c]) )
            iphas_r = np.concatenate( (iphas_r, p[i].data.field("rApermag3")[c]) ) 
            iphas_i = np.concatenate( (iphas_i, p[i].data.field("iApermag3")[c]) )

        # Did any stars pass the condition?
        if len(iphas_ra) == 0:
            flag_problem(full_filename, "NO_SUITABLE_STARS")
            continue

        # Attention: ra/dec is stored in radians in Eduardo's files!
        iphas_ra = np.degrees(iphas_ra)
        iphas_dec = np.degrees(iphas_dec)



        ######################
        # SDSS CROSS-MATCHING
        ######################

        # Reset
        r_shift, i_shift = "", ""
        r_std, i_std = "", ""
        iphas_match, sdss_match = [], []


        # Fetch the SDSS data in the same field
        sdss = get_sdss(min(iphas_ra)-0.01, max(iphas_ra)+0.01, 
                        min(iphas_dec)-0.01, max(iphas_dec)+0.01,
                        "AND r > 15 AND r < 18 AND i > 14.5 AND i < 18.5 AND score > 0.7")
        if len(sdss) == 0:
            logging.info("No SDSS counterparts found.")
        else:
            logging.info("Found %d SDSS sources in same field." % len(sdss))
            iphas_match, sdss_match = db.crossmatch(iphas_ra, iphas_dec, 
                                                    sdss["ra"], sdss["dec"],
                                                    0.5)

            if len(iphas_match) > 10:
                iphas_ra_match = iphas_ra[iphas_match]
                iphas_dec_match = iphas_dec[iphas_match]
                iphas_r_match = iphas_r[iphas_match]
                iphas_i_match = iphas_i[iphas_match]
                sdss_ra_match = sdss["ra"][sdss_match]
                sdss_dec_match = sdss["dec"][sdss_match]
                sdss_g_match = sdss["g"][sdss_match]
                sdss_r_match = sdss["r"][sdss_match]
                sdss_i_match = sdss["i"][sdss_match]

                # Write crossmatches to disk for further reference
                for n in range(len(iphas_match)):
                    csv_sdss.write( "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n" %
                                            (field, rundir,
                                            iphas_ra_match[n], iphas_dec_match[n], 
                                            iphas_r_match[n], iphas_i_match[n],
                                            sdss_ra_match[n], sdss_dec_match[n],
                                            sdss_g_match[n], sdss_r_match[n], 
                                            sdss_i_match[n]) )

                # Transform SDSS to IPHAS system using Gonzalez-Solares2011
                #comp_r = sdss_r_match - 0.144 + 0.006*(sdss_g_match - sdss_r_match)
                #comp_i = sdss_i_match - 0.411 - 0.073*(sdss_r_match - sdss_i_match)

                # Transform SDSS to IPHAS using Geert's equations
                #r_{IPHAS}[Vega] = r_{SDSS} -0.089 -0.021 (g_{SDSS} - r_{SDSS})
                #i_{IPHAS}[Vega] = i_{SDSS} -0.318 -0.079 (r_{SDSS} - i_{SDSS})
                comp_r = sdss_r_match - 0.089 - 0.021*(sdss_g_match - sdss_r_match)
                comp_i = sdss_i_match - 0.318 - 0.079*(sdss_r_match - sdss_i_match)

                # Compute shifts
                r_diff = iphas_r_match - comp_r
                i_diff = iphas_i_match - comp_i
                r_shift = np.round(np.median(r_diff), 3)
                i_shift = np.round(np.median(i_diff), 3)
                r_std = np.round(np.std(r_diff), 2)
                i_std = np.round(np.std(i_diff), 2)
                
                


       
        ######################
        # APASS CROSS-MATCHING
        ######################

        # Reset
        r_shift_apass, i_shift_apass = "", ""
        r_std_apass, i_std_apass = "", ""
        iphas_match, apass_match = [], []

        # Fetch the SDSS data in the same field
        apass = get_apass(  min(iphas_ra)-0.01, max(iphas_ra)+0.01, 
                            min(iphas_dec)-0.01, max(iphas_dec)+0.01,
                            """AND r > 13 AND r < 16.5 AND i > 12.5 AND i < 17
                               AND e_r BETWEEN 0 AND 0.1
                               AND e_i BETWEEN 0 AND 0.1""")
        if len(apass) == 0:
            logging.info("No APASS counterparts found.")
        else:
            logging.info("Found %d APASS sources in same field." % len(apass))
            iphas_match, apass_match = db.crossmatch(iphas_ra, iphas_dec, 
                                                    apass["ra"], apass["dec"],
                                                    1.0)

            if len(iphas_match) > 10:
                iphas_ra_match = iphas_ra[iphas_match]
                iphas_dec_match = iphas_dec[iphas_match]
                iphas_r_match = iphas_r[iphas_match]
                iphas_i_match = iphas_i[iphas_match]
                apass_ra_match = apass["ra"][apass_match]
                apass_dec_match = apass["dec"][apass_match]
                apass_g_match = apass["g"][apass_match]
                apass_r_match = apass["r"][apass_match]
                apass_i_match = apass["i"][apass_match]

                # Write crossmatches to disk for further reference
                for n in range(len(iphas_match)):
                    csv_apass.write( "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n" %
                                            (field, rundir,
                                            iphas_ra_match[n], iphas_dec_match[n], 
                                            iphas_r_match[n], iphas_i_match[n],
                                            apass_ra_match[n], apass_dec_match[n],
                                            apass_g_match[n], apass_r_match[n], 
                                            apass_i_match[n]) )

                # Transform SDSS to APASS using Christine's transforms
                comp_r = apass_r_match - 0.134 + 0.034*(apass_g_match - apass_r_match)
                comp_i = apass_i_match - 0.360 - 0.019*(apass_r_match - apass_i_match)

                # Compute shifts
                r_diff_apass = iphas_r_match - comp_r
                i_diff_apass = iphas_i_match - comp_i
                r_shift_apass = np.round(np.median(r_diff_apass), 3)
                i_shift_apass = np.round(np.median(i_diff_apass), 3)
                r_std_apass = np.round(np.std(r_diff_apass), 2)
                i_std_apass = np.round(np.std(i_diff_apass), 2)


        # Add a row for this field to the CSV file
        csv.write( ("%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n") % \
                    (field, rundir, run_r, run_i, run_ha,
                     len(sdss_match), 
                     r_shift, i_shift, 
                     r_std, i_std,
                     len(apass_match), 
                     r_shift_apass, i_shift_apass, 
                     r_std_apass, i_std_apass))
 
        csv.flush() # Sync CSV file to disk
        csv_sdss.flush()
        csv_apass.flush()

        p.close() # Close FITS
        

# Important: sync CSV files to disk
csv.close()
csv_errors.close()
