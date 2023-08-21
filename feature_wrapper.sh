#!/usr/bin/env bash
#set -x
echo "c o CALLSTR ${@}"

base_dir="/home/guests/cpriesne"
conda_location="${base_dir}/miniconda3"
conda_env_name="rb" # name of conda environment, default should be "rb"

EXTRACT=""
INSTANCE=""
EXT_FOLDER=""
FEAT=""
INSTANCE_FOLDER=""
COMBINED_FILE=""
LOG_LEVEL=""
RUN_LOCALLY="False"

while [[ $# -gt 0 ]]; do
  case $1 in
  -i | --instance)
    shift
    INSTANCE="${1}"
    shift
    ;;
  -e | --extract)
    shift
    EXTRACT="True"
    ;;
  -E | --ext_folder)
    shift
    EXT_FOLDER="${1}"
    shift
    ;;
  -f | --feat)
    shift
    FEAT="True"
    ;;
  -I | --instance_folder)
    shift
    INSTANCE_FOLDER="${1}"
    shift
    ;;
  -c | --combined_file)
    shift
    COMBINED_FILE="${1}"
    shift
    ;;
  -l | --log_level)
    shift
    LOG_LEVEL="${1}"
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


echo "c o ================= TEST ENV VARS ======================"
echo "c o ENV EXTRACT = ${EXTRACT}"
echo "c o ENV INSTANCE = ${INSTANCE}"
echo "c o ENV EXT_FOLDER = ${EXT_FOLDER}"
echo "c o ENV FEAT = ${FEAT}"
echo "c o ENV INSTANCE_FOLDER = ${INSTANCE_FOLDER}"
echo "c o ENV COMBINED_FILE = ${COMBINED_FILE}"
echo "c o ENV LOG_LEVEL = ${LOG_LEVEL}"
echo "c o ENV RUN_LOCALLY = ${RUN_LOCALLY}"

echo "c o ================= SET PRIM INTRT HANDLING ============"
function interrupted() {
  echo "c o Sending kill to subprocess"
  kill -TERM $PID
}
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

echo "c o ================= Building Command String ============"
cmd="python feature_runner.py"
if [[ -n "${EXTRACT}" ]]; then
  cmd+=" -extract"
fi
if [[ -n "${INSTANCE}" ]]; then
  cmd+=" -instance ${INSTANCE}"
fi
if [[ -n "${EXT_FOLDER}" ]]; then
  cmd+=" -ext_folder ${EXT_FOLDER}"
fi
if [[ -n "${FEAT}" ]]; then
  cmd+=" -feat"
fi
if [[ -n "${INSTANCE_FOLDER}" ]]; then
  cmd+=" -instance_folder ${INSTANCE_FOLDER}"
fi
if [[ -n "${COMBINED_FILE}" ]]; then
  cmd+=" -combined_file ${COMBINED_FILE}"
fi
if [[ -n "${LOG_LEVEL}" ]]; then
  cmd+=" -log_level ${LOG_LEVEL}"
fi
if [[ "${RUN_LOCALLY}" == "True" ]]; then
  cmd+=" -run_locally"
fi
echo "c o SOLVERCMD=$cmd"

echo "c o ================= Running Solver ====================="
myenv="TMPDIR=$TMPDIR"
#env $myenv $cmd >$tmpfile &
env $myenv $cmd &
PID=$!
wait $PID
exit_code=$?
echo "c o ================= Solver Done ========================"
echo "c o benchmark_wrapper: Solver finished with exit code=${exit_code}"
echo "c f RET=${exit_code}"

exit $exit_code
