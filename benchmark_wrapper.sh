#!/usr/bin/env bash
#set -x
echo "c o CALLSTR ${@}"

base_dir="/home/guests/cpriesne"
conda_location="${base_dir}/miniconda3"
conda_env_name="rb" # name of conda environment, default should be "rb"

ALGO=""
INSTANCE=""
PFILE=""
SUBSOLVER=""
RUN_ID=""
RUN_LOCALLY="False"

while [[ $# -gt 0 ]]; do
  case $1 in
  -a | --algo)
    shift
    ALGO="${1}"
    shift
    ;;
  -i | --instance)
    shift
    INSTANCE="${1}"
    shift
    ;;
  -p | --pfile)
    shift
    PFILE="${1}"
    shift
    ;;
  -s | --subsolver)
    shift
    SUBSOLVER="${1}"
    shift
    ;;
  -ri | --runid)
    shift
    RUN_ID="${1}"
    shift
    ;;
  -rl | --runlocally)
    shift
    RUN_LOCALLY="True"
    ;;
  *) # unknown argument
    echo "c o Unknown argument: ${1}"
    exit 1
    ;;
  esac
done

if [[ -z "${ALGO}" ]]; then
  echo "c o Please supply an algorithm"
  exit 1
fi
if [[ -z "${INSTANCE}" ]]; then
  echo "c o Please supply an instance file"
  exit 1
fi

echo "c o ================= TEST ENV VARS ======================"
echo "c o ENV ALGO = ${ALGO}"
echo "c o ENV INSTANCE = ${INSTANCE}"
echo "c o ENV PFILE = ${PFILE}"
echo "c o ENV SUBSOLVER = ${SUBSOLVER}"
echo "c o ENV RUN_ID = ${RUN_ID}"
echo "c o ENV RUN_LOCALLY = ${RUN_LOCALLY}"

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
cmd="python benchmark_runner.py ${ALGO} --instance ${INSTANCE}"
if [[ -n "${SUBSOLVER}" ]]; then
  cmd+=" --subsolver ${SUBSOLVER}"
fi
if [[ -n "${PFILE}" ]]; then
  cmd+=" --param_file ${PFILE}"
fi
if [[ -n "${RUN_ID}" ]]; then
  cmd+=" --run_id ${RUN_ID}"
fi
if [[ "${RUN_LOCALLY}" == "True" ]]; then
  cmd+=" --run_locally"
fi
echo "c o SOLVERCMD=$cmd"

echo "c o ================= Running Solver ====================="
myenv="TMPDIR=$TMPDIR"
env $myenv $cmd >$tmpfile &
PID=$!
wait $PID
exit_code=$?
echo "c o ================= Solver Done ========================"
echo "c o benchmark_wrapper: Solver finished with exit code=${exit_code}"
echo "c f RET=${exit_code}"

exit $exit_code
