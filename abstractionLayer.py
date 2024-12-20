################################################################################
#Date: April 19th, 2023                                                        #
#File: fndd.py                                                                 #
#Authour: Ben Haubrich                                                         #
#Synopsis: Convenience script for executing various actions for the application#
################################################################################
import argparse
import subprocess
from shutil import which, rmtree
from os import rename, remove, chdir, environ
from pathlib import Path
from platform import system
from getpass import getuser

def installProgram(systemName, programName):
   if systemName == 'Darwin':
      if None == which(programName):
         subprocess.run(["brew", "install", programName])
      elif systemName == 'Linux':
         if 'ninja' == programName:
            programName = 'ninja-build'
         if None == which(programName):
            subprocess.run(["sudo", "apt", "install", programName])

def setupForPlatform(systemName):
  rootPermissionRequired = False
  executableSuffix = '.elf'
  debugger = 'gdb'

  if systemName == 'Darwin':
      cxxCompiler = which('g++-12')
      cCompiler =  which('gcc-12')
      debugger = 'lldb'
      executableSuffix = '.Mach-O'
      #https://gist.github.com/scivision/d69faebbc56da9714798087b56de925a
      environ['SDKROOT'] = '/Library/Developer/CommandLineTools/SDKs/MacOSX13.1.sdk'

      requiredSoftware = ['gcc@12', 'cmake', 'ninja', 'git']
      for software in requiredSoftware:
         installProgram(systemName, software)

      return systemName, cCompiler, cxxCompiler, executableSuffix, debugger, rootPermissionRequired

  elif systemName == 'Linux':
      cxxCompiler = which('g++')
      cCompiler =  which('gcc')
      #In order to run the operating system on linux with the real-time scheduler settings you must run as root.
      rootPermissionRequired = True

      requiredSoftware = ['cmake', 'ninja', 'git']
      for software in requiredSoftware:
         installProgram(systemName, software)

      return systemName, cCompiler, cxxCompiler, executableSuffix, debugger, rootPermissionRequired

if __name__ == '__main__':

  parser = argparse.ArgumentParser(prog='abstractionLayer.py',
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
  systemName, cCompiler, cxxCompiler, executableSuffix, debugger, rootPermissionRequired = setupForPlatform(system())

  buildDirectoryName = systemName + '_build'
  cmakeBuildDirectory = Path(args.project_dir + '/' + buildDirectoryName)
  testFolderName = 'AbstractionLayer/AbstractionLayerTesting'

  if '\'clean\'' in args.command:
    if cmakeBuildDirectory.exists():
      rmtree(args.project_dir + '/' + buildDirectoryName)

  if '\'build\'' in args.command and '\'test\'' not in args.command:

    cmakeBuildDirectory.mkdir(parents=True, exist_ok=True)
    chdir(buildDirectoryName)

    if (args.build_type[0].strip('\'').lower() == 'debug'):
      subprocess.run(['cmake',
                      '-G Ninja',
                      '-DCMAKE_C_COMPILER=' + cCompiler,
                      '-DCMAKE_CXX_COMPILER=' + cxxCompiler,
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
                      '-S' + '../' + args.project_dir.strip('\'')])

    subprocess.run(['ninja'])

    chdir('..')

  if '\'test\'' in args.command:
    if (True == rootPermissionRequired and getuser() != 'root' and systemName == 'Linux'):
        print("The operating system module uses realtime scheduling which on this platform reuires root permission.")
        print("Please re-run as root (i.e. `sudo python3 abstractionLayer.py test`), use a different platform,")
        print("or create an operating system module that does not use realtime scheduling.")
        print("https://stackoverflow.com/questions/46874369/thread-explicit-scheduling-posix-api-gives-error")
        exit()
    chdir(testFolderName)

    subprocess.run(['cmake',
                    '-G Ninja',
                    '-DCMAKE_C_COMPILER=' + which(cCompiler),
                    '-DCMAKE_CXX_COMPILER=' + which(cxxCompiler),
                    '-S .'])
    subprocess.run(['ninja'])

    if ('\'All\'' in args.test_modules):
      subprocess.run(['ctest', '--output-on-failure', args.project_dir + testFolderName])
    else:
      for module in args.test_modules:
        subprocess.run(['ctest','--output-on-failure',  args.project_dir + testFolderName, '-R', module.strip('\'')])

    chdir('..')
