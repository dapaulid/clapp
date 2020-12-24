import os
import sys
import subprocess

def exec_win(cmd, output, shell):
	from winpty import PtyProcess
	if shell:
		cmd = 'cmd /C ' + cmd
	# end if
	proc = PtyProcess.spawn(cmd)
	try:	
		while True:
			char = proc.read(1)
			if not char:
				break
			# end if
			output(char)
		# end while
	except EOFError:
		pass
	# end try
	exitcode = proc.exitstatus
	proc.close()
	return exitcode
# end function

def exec_linux(cmd, output, shell):
	# TODO handle output
	return subprocess.call(cmd, shell=shell)	
# end function

def exec(cmd, output=sys.stdout.write, shell=False):
	if os.name == 'nt':
		return exec_win(cmd, output, shell)
	# end if
# end function

