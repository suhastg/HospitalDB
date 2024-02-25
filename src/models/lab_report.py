class Lab_Report:
    
    def __init__(self, report_id:int, patient_id:int, doctor_id:int, report_type:str, fee:float) -> None:
        self.report_id = report_id
        self.patient_id = patient_id
        self.doctor_id = doctor_id
        self.report_type = report_type
        self.fee = fee
