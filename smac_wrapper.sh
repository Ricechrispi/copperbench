#!/usr/bin/env bash
#set -x
echo "c o CALLSTR ${@}"

base_dir="/home/guests/cpriesne"
conda_location="${base_dir}/miniconda3"
conda_env_name="rb" # name of conda environment, default should be "rb"

ALGO=""
INSTANCE_FOLDER=""
TRIAL_TIMEOUT=""
N_TRIALS=""
N_WORKERS=""
OUTPUT_FOLDER=""
PFILE=""
SEED=""

while [[ $# -gt 0 ]]; do
  case $1 in
  -a | --algo)
    shift
    ALGO="${1}"
    shift
    ;;
  -i | --instance_folder)
    shift
    INSTANCE_FOLDER="${1}"
    shift
    ;;
  -i | --trial_timeout)
    shift
    TRIAL_TIMEOUT="${1}"
    shift
    ;;
  -i | --n_trials)
    shift
    N_TRIALS="${1}"
    shift
    ;;
  -i | --n_workers)
    shift
    N_WORKERS="${1}"
    shift
    ;;
  -i | --output_folder)
    shift
    OUTPUT_FOLDER="${1}"
    shift
    ;;
  -p | --param_file)
    shift
    PFILE="${1}"
    shift
    ;;
  -i | --seed)
    shift
    SEED="${1}"
    shift
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
if [[ -z "${INSTANCE_FOLDER}" ]]; then
  echo "c o Please supply an instance folder"
  exit 1
fi

echo "c o ================= TEST ENV VARS ======================"
echo "c o ENV ALGO = ${ALGO}"
echo "c o ENV INSTANCE_FOLDER = ${INSTANCE_FOLDER}"
echo "c o ENV TRIAL_TIMEOUT = ${TRIAL_TIMEOUT}"
echo "c o ENV N_TRIALS = ${N_TRIALS}"
echo "c o ENV N_WORKERS = ${N_WORKERS}"
echo "c o ENV OUTPUT_FOLDER = ${OUTPUT_FOLDER}"
echo "c o ENV PFILE = ${PFILE}"
echo "c o ENV SEED = ${SEED}"

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
cmd="python smac3_runner.py ${ALGO} --instance_folder ${INSTANCE_FOLDER}"
if [[ -n "${TRIAL_TIMEOUT}" ]]; then
  cmd+=" --trial_timeout ${TRIAL_TIMEOUT}"
fi
if [[ -n "${N_TRIALS}" ]]; then
  cmd+=" --n_trials ${N_TRIALS}"
fi
if [[ -n "${N_WORKERS}" ]]; then
  cmd+=" --n_workers ${N_WORKERS}"
fi
if [[ -n "${OUTPUT_FOLDER}" ]]; then
  cmd+=" --output_folder ${OUTPUT_FOLDER}"
fi
if [[ -n "${PFILE}" ]]; then
  cmd+=" --param_file ${PFILE}"
fi
if [[ -n "${SEED}" ]]; then
  cmd+=" --seed ${SEED}"
fi
echo "c o SMAC CMD=$cmd"

echo "c o ================= Running Smac ====================="
myenv="TMPDIR=$TMPDIR"
env $myenv $cmd >$tmpfile &
PID=$!
wait $PID
exit_code=$?
echo "c o ================= Smac Done ========================"
echo "c o smac3_wrapper: finished with exit code=${exit_code}"
echo "c f RET=${exit_code}"

exit $exit_code
