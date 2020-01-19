# anlin 2020
import argparse
import glob
import os
import fnmatch
import re
import sys
import subprocess

KS_DEFAULT_DIR_OSX = "/Applications/KISSlicer/"
KS_DEFAULT_DIR_WIN = "./"
KS_DEFAULT_FILENAME_OSX = "KISSLicer2.app/Contents/MacOS/KISSlicer"
KS_DEFAULT_FILENAME_WIN = "KISSlicer64.exe"
KS_PRINTER_DIR = "_printers"
KS_STYLE_DIR = "_styles"
KS_SUPPORT_DIR = "_supports"
KS_MATERIAL_DIR = "_materials"


def glob_nocase(dir, filemask):
	if not os.path.exists(dir):
		print("Directory not found ({0})".format(dir))
		return []
	rule = re.compile(fnmatch.translate(filemask), re.IGNORECASE)
	return [fname for fname in os.listdir(dir) if rule.match(fname)]
	
def basefilename(path):
	return os.path.splitext(os.path.basename(path))[0]
	
def listdir_basefilename(path):
	return [basefilename(filename) for filename in sorted(os.listdir(path), key=str.lower)]
	
def check_paths(base, names):
	for name in names:
		if not os.path.exists(base+"/"+name):
			return False
	return True
	
def replace_ext(filename, new_ext):
	return os.path.splitext(filename)[0]+"."+new_ext

def kiss_batch(args):
	if(args.ks_executable_path == ""):
		if(sys.platform == "darwin"):
			args.ks_executable_path = os.path.join(KS_DEFAULT_DIR_OSX, KS_DEFAULT_FILENAME_OSX)
		elif (sys.platform == "win32"):
			args.ks_executable_path = os.path.join(KS_DEFAULT_DIR_WIN, KS_DEFAULT_FILENAME_WIN)
		else:
			print("Unknown platform (Linux?), please specify KISSlicer executable path with -ks_path")
			sys.exit(0)
			
	if(args.ks_ini_dir == ""):
		if(sys.platform == "darwin"):
			args.ks_ini_dir = KS_DEFAULT_DIR_OSX
		elif (sys.platform == "win32"):
			args.ks_ini_dir = KS_DEFAULT_DIR_WIN
		else:
			print("Unknown platform (Linux?), please specify KISSlicer config path with -ini")
			sys.exit(0)
	
	args.in_dir = os.path.abspath(args.in_dir)
	args.out_dir = os.path.abspath(args.out_dir)
	args.ks_executable_path = os.path.abspath(args.ks_executable_path)
	args.ks_ini_dir = os.path.abspath(args.ks_ini_dir)
	
	if not os.path.isfile(args.ks_executable_path):
		print("KISSlicer executable not found")
		if(sys.platform == "darwin"):
			print("Note that you need to set ks_path to point to the actual executable if running on MacOS (eg. /Applications/KISSLicer2.app/Contents/MacOS/KISSlicer)")
		sys.exit(-1)
		
	if not check_paths(args.ks_ini_dir, [KS_PRINTER_DIR, KS_STYLE_DIR, KS_SUPPORT_DIR]):
		print("Config directories not found")
		
	if(args.out_dir == ""):
		args.out_dir = args.in_dir
		
	printer_profiles = listdir_basefilename(args.ks_ini_dir+"/"+KS_PRINTER_DIR)
	style_profiles = listdir_basefilename(args.ks_ini_dir+"/"+KS_STYLE_DIR)
	support_profiles = listdir_basefilename(args.ks_ini_dir+"/"+KS_SUPPORT_DIR)
	material_profiles = listdir_basefilename(args.ks_ini_dir+"/"+KS_MATERIAL_DIR)
	
	if(args.ks_printer > (len(printer_profiles)+1)):
		print("W: Invalid printer profile index")
		args.ks_printer = -1
	if(args.ks_style > (len(style_profiles)+1)):
		print("W: Invalid style profile index")
		args.ks_style = -1
	if(args.ks_support > (len(support_profiles)+1)):
		print("W: Invalid support profile index")
		args.ks_style = -1		
	if(args.ks_material > (len(material_profiles)+1)):
		print("W: Invalid support profile index")
		args.ks_style = -1		
	
	if(args.list):
		print("Printer profiles:")
		for index, name in enumerate(printer_profiles):
			print("    {0}: {1}".format(index+1, name))
		print("\n\nStyle profiles:")
		for index, name in enumerate(style_profiles):
			print("    {0}: {1}".format(index+1, name))
		print("\n\nSupport profiles:")
		for index, name in enumerate(support_profiles):
			print("    {0}: {1}".format(index+1, name))
		print("\n\nMaterial profiles:")
		for index, name in enumerate(material_profiles):
			print("    {0}: {1}".format(index+1, name))
	
	stl_files = glob_nocase(args.in_dir, "*.stl")
	if(len(stl_files) == 0):
		print("No STLs found")
		sys.exit(0)
	

	kiss_base_args = [args.ks_executable_path, "-single", "-hidegui", "-inidir \"{0}/\"".format(args.ks_ini_dir)]
	kiss_profile_args = []
	if(args.ks_printer > 0):
		kiss_profile_args.append("-printer {0}".format(args.ks_printer))
	if(args.ks_style > 0):
		kiss_profile_args.append("-style {0}".format(args.ks_style))
	if(args.ks_support > 0):
		kiss_profile_args.append("-support {0}".format(args.ks_support))		
	if(args.ks_material > 0):
		kiss_profile_args.append("-ext1mat \"{0}\"".format(material_profiles[args.ks_material-1]))		
		
	print("\nPrinter profile: {0}".format(printer_profiles[args.ks_printer-1] if (args.ks_printer > 0) else "default"))
	print("Style profile: {0}".format(style_profiles[args.ks_style-1] if (args.ks_style > 0) else "default"))
	print("Support profile: {0}".format(support_profiles[args.ks_support-1] if (args.ks_support > 0) else "default"))
	print("Material profile: {0}".format(material_profiles[args.ks_material-1] if (args.ks_material > 0) else "default"))

	print("\nFound {0} STLs".format(len(stl_files)))
	if(args.dry_run):
		sys.exit(0)
	print("\nRunning KISSlicer".format(len(stl_files)))
	for index, stl in enumerate(stl_files):
		stl_path = os.path.join(args.in_dir, stl)
		gcode_path = os.path.join(args.out_dir, replace_ext(stl, "gcode"))
		kiss_stl_args = ["-o \"{0}\"".format(gcode_path), "\"{0}\"".format(stl_path)]
		print("    {0}/{1}: {2}".format(index+1, len(stl_files), stl))
		print(" ".join(kiss_base_args + kiss_profile_args + kiss_stl_args))
		os.system(" ".join(kiss_base_args + kiss_profile_args + kiss_stl_args))



def main():
	print("KISSlicer batch tool")
	parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
	parser.add_argument("in_dir", type=str, help="Input directory")
	parser.add_argument("-out", dest="out_dir", type=str, default="", help="Output directory")	  
	parser.add_argument("-ini", dest="ks_ini_dir", type=str, default="", help="Config INI directory")	
	parser.add_argument("-printer", dest="ks_printer", type=int, default=-1, help="Printer profile (1...N)")
	parser.add_argument("-style", dest="ks_style", type=int, default=-1, help="KISSlicer style profile (1...N)")
	parser.add_argument("-support", dest="ks_support", type=int, default=-1, help="KISSlicer support profile (1...N)")
	parser.add_argument("-material", dest="ks_material", type=int, default=-1, help="KISSlicer material profile (1...N)")
	parser.add_argument("-ks-executable-path", dest="ks_executable_path", type=str, default="", help="Path to KISSlicer2 executable")
	parser.add_argument("-list-profiles", dest="list", action="store_true", help="List printer, style and support profiles")
	parser.add_argument("-dry-run", dest="dry_run", action="store_true", help="Perform a dry run")
	args = parser.parse_args()
	kiss_batch(args)

#############################################################s
if __name__=="__main__":
	main()