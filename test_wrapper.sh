#!/usr/bin/env bash
#set -x
echo "c o CALLSTR ${@}"

base_dir="/home/guests/cpriesne"
conda_location="${base_dir}/miniconda3"
conda_env_name="rb" # name of conda environment, default should be "rb"

echo "c o ================= SET PRIM INTRT HANDLING ============"
function interrupted() {
  echo "c o Sending kill to subprocess"
  kill -TERM $PID
  echo "c o Removing tmp files"
  [ ! -z "$tmpfile" ] && rm $tmpfile
}
function finish {
  echo "c o Removing tmp files"
  [ ! -z "$tmpfile" ] && rm $tmpfile
}
trap finish EXIT
trap interrupted TERM
trap interrupted INT

echo "c o ================= Changing directory ==================="
cd "${base_dir}/master_project"
if [[ $? -ne 0 ]]; then
  echo "c o Could not change directory to ${base_dir}/master_project. Exiting..."
  exit 1
fi

echo "c o ================= Activating Conda environment ======================"
# !! Contents within this block are managed by 'conda init' !!
__conda_setup="$('${conda_location}/bin/conda' 'shell.bash' 'hook' 2>/dev/null)"
if [ $? -eq 0 ]; then
  eval "$__conda_setup"
else
  if [ -f "${conda_location}/etc/profile.d/conda.sh" ]; then
    . "${conda_location}/etc/profile.d/conda.sh"
  else
    export PATH="${conda_location}/bin:$PATH"
  fi
fi
unset __conda_setup
conda activate "$conda_env_name"

echo "c o ================= Preparing tmpfiles ================="
tmpfile=$(mktemp /run/shm/result.XXXXXX)

echo "c o ================= Building Command String ============"
cmd="python tests/nesthdb_tests.py"
echo "c o SOLVERCMD=$cmd"

echo "c o ================= Running Unit tests ====================="
myenv="TMPDIR=$TMPDIR"
env $myenv $cmd >$tmpfile &
PID=$!
wait $PID
exit_code=$?
echo "c o ================= Unit tests Done ========================"
echo "c o test_wrapper: tests finished with exit code=${exit_code}"
echo "c f RET=${exit_code}"

exit $exit_code
