import re

import os
import signal
import subprocess

import time
from decouple import config

from quizsys.settings import CODE_PATH


def grade_question(question, response, file_suffix=None):
    if question.type == 'MCQ':
        correct_choices = question.choices.filter(is_correct_answer=True)
        correct_choice_pks = sorted([str(choice.pk) for choice in correct_choices])
        correct_choices_str = ';'.join(correct_choice_pks)

        response = ";".join(sorted(response.split(";")))
        return {"status": response == correct_choices_str}
    if question.type == 'FIB':
        status = False
        accepted_answers = question.answers
        for accepted_answer in accepted_answers.all():
            if response == accepted_answer.content:
                status = True
        return {"status": status}

    # question.type == "COD" - coding question

    if re.search(r"import\s+os", response) or re.search(r"import\s+subprocess", response):
        return {"status": False}

    code = get_code(question, response)
    if code == "":
        return {"status": False}

    if not os.path.exists(CODE_PATH):
        os.makedirs(CODE_PATH)

    status = True
    testcases = question.testcases.all()

    for testcase in testcases:
        input = testcase.input.replace("\n", "\\n").replace("\t", "\\t")
        output = testcase.output
        header = "import sys\nimport io\nsys.stdin = io.StringIO(\"%s\")\n" % input
        extended_code = header + code

        script_path = os.path.join(CODE_PATH, "script_" + str(file_suffix) + ".py")
        with open(script_path, 'w') as f:
            f.write(extended_code)

        submitted_output = run_script(script_path)
        if submitted_output != output.strip():
            status = False

    return {'status': status}


def run_script(script_path):
    command = 'python ' + script_path

    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    time.sleep(1)
    if proc.poll() is None:
        proc.kill()
    os.remove(script_path)
    submitted_output = proc.stdout.read().strip().decode('utf-8')
    return submitted_output

    # completed = subprocess.run(['python', script_path], timeout=1, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    # if completed.stdout.decode('utf-8').strip() != output.strip():
    #     status = False
    #     break

    # with subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, preexec_fn=os.setsid) as process:
    #     try:
    #         output = process.communicate(timeout=1)[0]
    #     except subprocess.TimeoutExpired:
    #         os.killpg(process.pid, signal.SIGINT)
    #         output = process.communicate()[0]
    #
    # print (output)


def get_code(question, response):
    if not question.extra or question.extra == "":
        return response

    code = question.extra
    fill_ins = response.split(";")
    blanks = re.findall(r'___+', code)
    if len(fill_ins) != len(blanks):
        return ""

    for i in range(len(blanks)):
        code = code.replace(blanks[i], fill_ins[i], 1)
    return code



