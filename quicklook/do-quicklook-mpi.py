"""
Create quicklook versions of all IPHAS fields

This script is written for MPI, i.e. execute using:
mpirun -np 4 python do-quicklook-mpi.py

"""
import pyfits
import logging
import quicklook
import sys
import os
from mpi4py import MPI



IPHASQC = '/home/gb/dev/iphas-qc/qcdata/iphas-qc.fits'

# Setup MPI and logging
comm = MPI.COMM_WORLD
# Define the messages we'll be passing through MPI
TAG_GIVE_WORK = 801  # Worker waiting for instructions


logging.basicConfig(level=logging.DEBUG, 
    format="%(asctime)s/W"+str(comm.rank)+"/"+MPI.Get_processor_name()+"/%(levelname)s: %(message)s", 
    datefmt="%Y-%m-%d %H:%M:%S" )

""" Setup logging """
"""
log = logging.getLogger('quicklook')
fmt = logging.Formatter('%(asctime)s/W'+str(comm.rank)+'/'+MPI.Get_processor_name()+'/%(levelname)s: %(message)s',
                                datefmt='%Y-%m-%d %H:%M:%S')

screen = logging.StreamHandler(stream=sys.stdout)
screen.setLevel(logging.INFO)
screen.setFormatter(fmt)   
log.addHandler(screen)

logfile = logging.FileHandler('log.txt')
logfile.setLevel(logging.DEBUG)
logfile.setFormatter(fmt)
log.addHandler(logfile)
"""

def mpi_master():
    """
    Distributes the work

    """
    logging.info("Running on %d cores" % comm.size)

    qc = pyfits.getdata(IPHASQC, 1)
    fields = qc.field('id')

    if os.path.exists('quicklook.done'):
        fields_done = [field.strip() for field in open('quicklook.done', 'r').readlines()]
    else:
        fields_done = []

    done = open('quicklook.done', 'a')

    for field in fields:
        if field in fields_done:
            continue

        # Wait for a worker to report for duty
        rank_done = comm.recv(source=MPI.ANY_SOURCE, tag=TAG_GIVE_WORK)
        # Send the worker the details of the next field
        comm.send(field, dest=rank_done)
        logging.info('Field %s sent to worker %s' % (field, rank_done))
        done.write('%s\n' % field)
        done.flush()

    done.close()

    # Tell all workers we're finished
    for worker in range(1, comm.size):
        comm.send("FINISHED", dest=worker)

    return

def mpi_worker():
    """
    Carries out the work.

    """
    while True:
        # Ask for work
        comm.send(comm.rank, dest=0, tag=TAG_GIVE_WORK)
        msg = comm.recv(source=0)
        if msg == "FINISHED":
            return

        # Perform work
        logging.debug("Message rcvd: \"%s\"" % msg)

        ql = quicklook.Quicklook(msg)
        ql.run()

def mpi_run():
    """
    Main function.

    """
    if comm.rank == 0:
        mpi_master()
    else:
        mpi_worker()
    return

""" MAIN EXECUTION """
if __name__ == "__main__":
    mpi_run()
