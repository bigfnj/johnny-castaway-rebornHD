"""Reuse the frozen no-window Docker launcher after checking runtime Git identity."""
import importlib.util
import subprocess
import contract as c

FROZEN=c.OBSERVER.parent/'run.py'
FROZEN_SHA='4e7cbfe22aafcf8ba64185852f756b65199a3c0ae189cf2207b02217462004c6'

def main():
    # Art commits may follow the selected runtime commit; native code must match it.
    flags=getattr(subprocess,'CREATE_NO_WINDOW',0)
    subprocess.run(['git','-C',str(c.ROOT),'merge-base','--is-ancestor',c.RUNTIME_COMMIT,'HEAD'],check=True,creationflags=flags)
    diff=subprocess.check_output(['git','-C',str(c.ROOT),'diff',c.RUNTIME_COMMIT,'--','src','platform','third_party/miniz','CMakeLists.txt'],creationflags=flags)
    c.require(not diff,'runtime matches authorized '+c.RUNTIME_COMMIT)
    c.require(c.sha(FROZEN.read_bytes())==FROZEN_SHA,'frozen no-window launcher')
    spec=importlib.util.spec_from_file_location('final_native_launch',FROZEN)
    launcher=importlib.util.module_from_spec(spec);spec.loader.exec_module(launcher)
    launcher.HERE=c.HERE;launcher.main()

if __name__=='__main__':main()
