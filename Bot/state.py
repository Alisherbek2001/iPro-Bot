from aiogram.fsm.state import StatesGroup, State

class ChangeLanguageForm(StatesGroup):
    language_change = State() 
    

class Form(StatesGroup):
    language = State()
    channel_selection = State() 
    ad_type = State()     
           
    employee_skills = State()    
    employee_firm_name = State() 
    employee_activity = State()   
    employee_contact_person = State() 
    employee_phone = State()
    employee_region = State()     
    employee_contact_time = State() 
    employee_work_time = State() 
    employee_salary = State()     
    employee_additional = State() 

    job_name = State()           
    job_age = State()           
    job_profession = State()     
    job_experience = State()    
    job_phone = State()          
    job_region = State()         
    job_expected_salary = State() 
    job_additional = State()     

    partner_name = State()       
    partner_activity_type = State()
    partner_region = State()    
    partner_phone = State()       
    partner_additional = State()   

    confirm = State()
    
class Form_Check(StatesGroup):
    waiting_confirmation = State()
    waiting_approval = State()