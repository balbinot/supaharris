import numpy
from matplotlib import pyplot


def parse_bica_2019_refs(fname="./MW_GCS_Bica2019/refs.dat", debug=False):
    if not os.path.isfile(fname) or not os.path.exists(fname):
        print("ERROR: file not found: {0}".format(fname))
        return

def parse_bica_2019_table2(fname="./MW_GCS_Bica2019/table2.dat", debug=False):
    if not os.path.isfile(fname) or not os.path.exists(fname):
        print("ERROR: file not found: {0}".format(fname))
        return


def parse_bica_2019_table3(fname="./MW_GCS_Bica2019/table3.dat.gz", debug=False):
    if not os.path.isfile(fname) or not os.path.exists(fname):
        print("ERROR: file not found: {0}".format(fname))
        return


def parse_bica_2019_table4(fname="./MW_GCS_Bica2019/table4.dat", debug=False):
    if not os.path.isfile(fname) or not os.path.exists(fname):
        print("ERROR: file not found: {0}".format(fname))
        return


def parse_bica_2019_table5(fname="./MW_GCS_Bica2019/table5.dat", debug=False):
    if not os.path.isfile(fname) or not os.path.exists(fname):
        print("ERROR: file not found: {0}".format(fname))
        return



if __name__ == "__main__":
    refs = parse_bica_2019_refs(debug=True)
    t2 = parse_bica_2019_table2(debug=True)
    t3 = parse_bica_2019_table3(debug=True)
    t4 = parse_bica_2019_table4(debug=True)
    t5 = parse_bica_2019_table5(debug=True)
