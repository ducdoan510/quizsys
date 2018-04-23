import re

import os
import signal
import subprocess

import time
from decouple import config

from quizsys.settings import CODE_PATH


def grade_question(question, response, file_suffix=None, sample_test=False):
    if question.type == 'MCQ':
        correct_choices = question.choices.filter(is_correct_answer=True)
        correct_choice_pks = sorted([str(choice.pk) for choice in correct_choices])
        correct_choices_str = ';'.join(correct_choice_pks)

        response = ";".join(sorted(response.split(";")))
        return {"status": response == correct_choices_str}
    if question.type == 'FIB':
        status = False
        accepted_answers = question.answers
        accepted_answers_content = [accepted_answer.content for accepted_answer in accepted_answers.all()]
        for accepted_answer in accepted_answers_content:
            if response == accepted_answer:
                status = True
        return {"status": status}

    # question.type == "COD" - coding question

    if re.search(r"import\s+os", response) or re.search(r"import\s+subprocess", response):
        return {"status": False}

    if not os.path.exists(CODE_PATH):
        os.makedirs(CODE_PATH)

    status = True
    testcases = question.testcases.all()
    if sample_test:
        testcases = testcases[:3]
    else:
        testcases = testcases[3:]

    failed_testcases = []
    errors = set([])

    code = get_code(question, response)
    if code == "":
        return {"status": False, "extra_info": ";".join([str(tc.pk) for tc in testcases])}

    for testcase in testcases:
        # input = testcase.input.replace("\n", "\\n").replace("\t", "\\t")
        output = testcase.output
        # header = "import sys\nimport io\nsys.stdin = io.StringIO(\"%s\")\n" % input
        # extended_code = header + code
        extended_code = code

        script_path = os.path.join(CODE_PATH, "script_" + str(file_suffix) + ".py")
        with open(script_path, 'w') as f:
            f.write(extended_code)

        submitted_output, submitted_error = run_script(script_path, testcase.input)
        if submitted_output != output.strip():
            failed_testcases.append(testcase.pk)
            errors.add(submitted_error)
            status = False

    return {
        'status': status,
        'extra_info': ";".join([str(testcase_pk) for testcase_pk in failed_testcases]),
        'code_errors': "; ".join(list(errors)),
        'score': (testcases.count() - len(failed_testcases)) * 1.0 / testcases.count()
    }


def run_script(script_path, input=""):
    command = ["python", script_path]
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
    # time.sleep(1)
    try:
        submitted_output, submitted_error = proc.communicate(input.encode('utf-8'), timeout=5)
    except subprocess.TimeoutExpired:
        print("subprocess.TimeoutExpired")
        return "", "RuntimeError: Your program may not terminate"
    # if proc.poll() is None:
    #     proc.kill()
    os.remove(script_path)
    # submitted_output = proc.stdout.read().strip().decode('utf-8')
    # submitted_error = proc.stderr.read().strip().decode('utf-8')
    submitted_output = submitted_output.decode('utf-8').strip()
    submitted_error = submitted_error.decode('utf-8').strip()
    if submitted_error != "":
        submitted_error = submitted_error.split("\n")[-1]
    return submitted_output, submitted_error


def get_code(question, response):
    if not question.extra or question.extra == "" or len(re.findall(r'___+', question.extra)) == 0:
        return response

    code = question.extra
    fill_ins = response.split(";")
    blanks = re.findall(r'___+', code)
    if len(fill_ins) != len(blanks):
        return ""

    for i in range(len(blanks)):
        code = code.replace(blanks[i], fill_ins[i], 1)
    return code
