import json
from pathlib import Path

academic = "undergraduate-academic-policies"

original_questions = [
    ("001", "Can I take more than 36 credits in one semester", ["3.3.7"], [5], ["0018"]),
    ("002", "If I fail a course, can I retake it?", ["3.20.1"], [15, 16], ["0077"]),
    ("003", "Will withdrawing from a course affect my GPA?", ["3.3.12"], [5], ["0022"]),
    ("004", "What happens if I miss too many classes?", ["3.4.2", "3.4.3", "3.4.4", "3.4.5"], [6], ["0023", "0024", "0025"]),
    ("005", "How many semesters can I stay on academic probation?", ["3.16.4", "3.16.5"], [14], ["0067"]),
]

questions = []
for question_id, text, sections, pages, chunk_numbers in original_questions:
    questions.append({
        "question_id": question_id,
        "question": text,
        "language": "en",
        "source": "generated",
        "group": "answerable",
        "expected_sections": sections,
        "expected_pages": pages,
        "relevant_chunk_ids": [f"{academic}-{number}" for number in chunk_numbers],
    })

# Each row contains the question, language, group, supporting chunks, and notes.
student_questions = [
    (
        "if my adviser is on annual summer leave, then will he able to respond to my student request in registrar only when he comes back?",
        "en", "unanswerable", [],
        "The corpus does not describe adviser coverage or response times during annual leave.",
    ),
    (
        "What should I do if I didn’t receive EDMS contract signing yet?",
        "en", "unanswerable", [],
        "Ask what type of contract it is and when the signing request was expected.",
    ),
    (
        "кому обратиться если не получается подписать договор?",
        "ru", "unanswerable", [],
        "Ask what type of contract it is and what happens when the student tries to sign.",
    ),
    (
        "How can I contact school office to request for excusal from classes? did not get an answer from seds gmail",
        "en", "partial", [f"{academic}-0026"],
        "The instructor approves the absence. A SEDS contact or follow-up channel was not found.",
    ),
    (
        "Who can I ask about withdrawal of an internship?",
        "en", "unanswerable", [],
        "Ask what type of internship it is and whether it is already registered.",
    ),
    (
        "What should I do if I unsubscribe from the seds, all students and campus 22 in gmail",
        "en", "unanswerable", [],
        "No instructions for restoring these subscriptions were found.",
    ),
    (
        "Where can I get the certificate that i study in the uni? I need it for the visa.",
        "en", "unanswerable", [],
        "The mobility guidebook mentions enrollment verification but does not explain where to obtain it for a visa.",
    ),
    (
        "is there a site or page to know what could be counted as an excused absence and what documents are needed?",
        "en", "partial", [f"{academic}-0023", f"{academic}-0025", f"{academic}-0026"],
        "The policies describe attendance and approval. A single page listing qualifying reasons and required documents was not found.",
    ),
    (
        "where can I get the certificate of illness?",
        "en", "unanswerable", [],
        "Ask whether the certificate is for a class absence or for medical leave.",
    ),
    (
        "Где можно цены на дорм посмотреть?",
        "ru", "answerable", ["dormitory-accommodation-rules-0022"],
        "Section 3.1.10, page 5, identifies MyNU as the place to check approved rates. Local corpus only.",
    ),
    (
        "У нас в университете есть Erasmus программы, или какие то государственные программы по обмену, где все оплачивается полностью?",
        "ru", "partial", ["academic-mobility-guidebook-2026-0017", "student-mobility-policy-0037"],
        "The sources mention Erasmus+ and government-funded programs. Full coverage depends on the specific opportunity.",
    ),
    (
        "Придет ли стипендия если карта просрочилась?",
        "ru", "unanswerable", [],
        "The corpus does not explain how an expired card affects payment. The bank account and payment details matter.",
    ),
    (
        "к кому можно обратиться по поводу неисправных тренажеров в джиме?",
        "ru", "answerable", ["sports-complex-rules-0093"],
        "Clause 96 says to report equipment malfunctions to the Sports Complex administration.",
    ),
    (
        "is it possible to get an excused absence if youre going to a conference? if so, how do you do it?",
        "en", "partial", [f"{academic}-0026"],
        "The instructor approves absences. A conference-specific rule and document list were not found.",
    ),
    (
        "Where can we complain about dormitory service?",
        "en", "unanswerable", [],
        "A general complaint channel was not found. Ask what the service issue concerns.",
    ),
    (
        "If I want to change schools should I request it in registrar now?",
        "en", "partial", [f"{academic}-0035", f"{academic}-0036"],
        "The sources describe eligibility and the Transfer between Schools form in SIS. They do not establish whether applications are open now.",
    ),
    (
        "Will I be able to leave my belongings in the dormitory after I receive confirmation of my withdrawal? (Summer course)",
        "en", "unanswerable", [],
        "Rules about leaving NU or eviction do not establish what happens after withdrawing from a single summer course.",
    ),
    (
        "are there any financial obligations if a student drops out of the university after 2nd year?",
        "en", "unanswerable", [],
        "Ask which obligations the student means and what funding or contract terms apply.",
    ),
    (
        "are there any limitation on the number of credits you can take on summer?",
        "en", "unanswerable", [],
        "An explicit Summer term maximum was not found. The ordinary semester limit alone does not establish it.",
    ),
    (
        "кому писать репорт если мою айдишку забрали и воспользовались?",
        "ru", "partial", ["campus-access-security-rules-0013"],
        "The lost-card reporting procedure applies. A specific channel for reporting misuse was not found.",
    ),
    (
        "если экстра плейс одобрили, но в расписании уже 36 кредитов, нужно дропнуть курс чтобы место для него было? типа автоматом зарегается или как? подскажите пожалуйста",
        "ru", "partial", ["undergraduate-academic-policies-0018", "undergraduate-academic-policies-0019"],
        "The sources explain the credit limit and overload process. They do not explain extra-place auto-registration.",
    ),
    (
        "Что можно сделать если проф в регистраре неправильную оценку поставил? Это же окончательно? Если окончательно куда можно заяву накатать на него? Подскажите пожалуйста",
        "ru", "answerable", ["undergraduate-academic-policies-0072", "undergraduate-academic-policies-0073", "undergraduate-academic-policies-0074", "undergraduate-academic-policies-0075", "undergraduate-academic-policies-0076"],
        "Incorrect grade entry is grounds for appeal. The procedure depends on whether it is an exam grade or a final course grade.",
    ),
    (
        "Как можно запустить на кампус родственников? И что им нужно с собой иметь? Подскажите пожалуйста",
        "ru", "partial", ["campus-access-security-rules-0014", "campus-access-security-rules-0015"],
        "Security may ask for identification and access documents. The booking procedure for student relatives was not confirmed.",
    ),
    (
        "Подскажите пожалуйста гостей на кампус пускают без запроса секюрити?",
        "ru", "partial", ["campus-access-security-rules-0040"],
        "The security request applies to the visitor category described in the source. A general rule for student guests was not confirmed.",
    ),
    (
        "Можете подсказать, имеет ли проф право ставить F за курс из за низкого attendance-a?",
        "ru", "partial", ["undergraduate-academic-policies-0025"],
        "Attendance may affect the grade. The source does not explicitly authorize an F for low attendance.",
    ),
    (
        "подскажите где можно найти документ где написаны правила как составляются силлабусы, какие полиси профы могут делать и тд?",
        "ru", "partial", ["undergraduate-academic-policies-0025"],
        "The source states an attendance disclosure requirement. A general syllabus policy was not found.",
    ),
    (
        "подскажите, пожалуйста, а магистранты тоже получают дорожку (state grant)?",
        "ru", "unanswerable", [],
        "Clarify whether this means travel reimbursement, an educational grant, or another payment.",
    ),
    (
        "Подскажите, пожалуйста, как заполнять форму overload, если курс будет регистрироваться через extra place и его пока нет в расписании?",
        "ru", "partial", ["undergraduate-academic-policies-0018", "undergraduate-academic-policies-0019"],
        "The sources explain where to submit the form and who approves it. Instructions for an extra-place course were not found.",
    ),
    (
        "Подскажите, пожалуйста, у кого можно получить справку об absence of academic and non-academic misconducts?",
        "ru", "unanswerable", [],
        "The corpus does not identify who issues this certificate.",
    ),
    (
        "не подскажете как нужно делать retake по курсам? Как и когда заполнять форму?",
        "ru", "partial", ["undergraduate-academic-policies-0077", "undergraduate-academic-policies-0078"],
        "The policy describes retake eligibility and grading. The form and submission deadlines were not found.",
    ),
]

needs_review = {"real-007", "real-009", "real-019"}
contract_questions = {"real-002", "real-003"}

for number, (text, language, group, relevant_ids, notes) in enumerate(student_questions, start=1):
    question_id = f"real-{number:03d}"
    question = {
        "question_id": question_id,
        "question": text,
        "language": language,
        "source": "real_student",
        "group": group,
        "relevant_chunk_ids": relevant_ids,
        "notes": notes,
    }

    if question_id in needs_review:
        question["label_status"] = "needs_review"

    if question_id in contract_questions:
        question["topic"] = "contract_signing"

    questions.append(question)

output_path = Path("data/eval/questions.json")
output_path.parent.mkdir(parents=True, exist_ok=True)

with output_path.open("w", encoding="utf-8") as json_file:
    json.dump(questions, json_file, ensure_ascii=False, indent=2)

print(f"Saved {len(questions)} questions to {output_path}")