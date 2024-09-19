################################################################################
#Date: April 19th, 2023                                                        #
#File: fndd.py                                                                 #
#Authour: Ben Haubrich                                                         #
#Synopsis: An analog to idf.py for desktop builds (FouNDationDesktop.py)       #
#          Provides convenience, but also provides the ability to constrain the#
#          way in which developers build and run the executable instead of     #
#          providing the raw tools and leaving it up to them                   #
################################################################################
import argparse
import subprocess
from shutil import which, rmtree
from os import rename, remove, chdir
from pathlib import Path
from platform import system

def setCCompiler():
  systemName = system()
  if systemName == 'Darwin':
      return which('gcc-12')
  elif systemName == 'Linux':
      return which('gcc')

def setCxxCompiler():
  systemName = system()
  if systemName == 'Darwin':
      return which('g++-12')
  elif systemName == 'Linux':
      return which('g++')

if __name__ == '__main__':

  parser = argparse.ArgumentParser(prog='fndd.py',
                                       description='Run cmake projects on a desktop',
                                       epilog='Created by Ben Haubrich April 19th, 2024')
  #This first positional argument holds one or more arguments (nargs='+') so that when new positional commands are add below
  #They are contained within the list of arguments for the first positional argument. In this way, a list of possible
  #commands can be searched through by the name of the commands given.
  parser.add_argument('command', type=ascii, nargs='+', default='None',
                          help=argparse.SUPPRESS
                     )

  parser.add_argument('clean', type=ascii, nargs='?', default='None',
                          help='Clean up the files from the last build'
                     )
  parser.add_argument('build', type=ascii, nargs='?', default='None',
                          help='Build the project in the selected directory'
                     )
  parser.add_argument('test', type=ascii, nargs='?', default='None',
                          help='Run built-in module unit tests'
                     )

  parser.add_argument('-c', '--project-dir', default='.',
                    help='The directory to build the project which contains a top-level CMakeLists.txt. Defaults to current directory'
                    )
  parser.add_argument('-t', '--test-modules', nargs='+', type=ascii, default="All",
                    help='Test modules listed. Defaults to "All". Valid modules share the same name as the directory name'
                    )
  parser.add_argument('-b', '--build-type', nargs='+', type=ascii, default="Debug",
                    help='Build version to build. Defaults to "Debug"'
                    )

  args = parser.parse_args()

  #Uncomment for help with debugging.
  #print("{}".format(args))
  buildFolderName = system() + '_build'
  testFolderName = 'AbstractionLayer/AbstractionLayerTesting'
  cCompiler = setCCompiler()
  cxxCompiler = setCxxCompiler()

  path = Path(args.project_dir + '/' + buildFolderName)

  if '\'clean\'' in args.command:
    if path.exists():
      rmtree(args.project_dir + '/' + buildFolderName)

  if '\'build\'' in args.command and '\'test\'' not in args.command:

    path.mkdir(parents=True, exist_ok=True)
    chdir(buildFolderName)

    if (args.build_type[0].strip('\'').lower() == 'debug'):
      subprocess.run(['cmake',
                      '-G Ninja',
                      '-DCMAKE_C_COMPILER=' + cCompiler,
                      '-DCMAKE_CXX_COMPILER=' + cxxCompiler,
                      '-DDEBUG_BUILD=1',
                      '-S' + '../' + args.project_dir.strip('\'')])
    elif (args.build_type[0].strip('\'').lower() == 'release'):
      subprocess.run(['cmake',
                      '-G Ninja',
                      '-DCMAKE_C_COMPILER=' + cCompiler,
                      '-DCMAKE_CXX_COMPILER=' + cxxCompiler,
                      '-DRELEASE_BUILD=1',
                      '-S' + '../' + args.project_dir.strip('\'')])
    else:
      subprocess.run(['cmake',
                      '-G Ninja',
                      '-DCMAKE_C_COMPILER=' + cCompiler,
                      '-DCMAKE_CXX_COMPILER=' + cxxCompiler,
                      '-DDEBUG_BUILD=1',
                      '-S' + '../' + args.project_dir.strip('\'')])

    subprocess.run(['ninja'])

    chdir('..')

  if '\'test\'' in args.command:
    chdir(testFolderName)

    subprocess.run(['cmake',
                    '-G Ninja',
                    '-DCMAKE_C_COMPILER=' + which('gcc-12'),
                    '-DCMAKE_CXX_COMPILER=' + which('g++-12'),
                    '-S .'])
    subprocess.run(['ninja'])

    if ('\'All\'' in args.test_modules):
      subprocess.run(['ctest', '--output-on-failure', args.project_dir + testFolderName])
    else:
      for module in args.test_modules:
        subprocess.run(['ctest','--output-on-failure',  args.project_dir + testFolderName, '-R', module.strip('\'')])

    chdir('..')
