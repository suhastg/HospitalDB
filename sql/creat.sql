CREATE TABLE Patient
(
p_id int AUTO_INCREMENT PRIMARY key,
name varchar(35), 
address varchar(35),
gender varchar(10) 
);

CREATE TABLE doctor
(
    name varchar(30),
    doctor_id int primary key,
    dept varchar(20)
);

CREATE TABLE lab_report
(
    p_id int,
    lab_no int primary key,
    amount int,
    doctor_id int,
    report_date date,
    foreign key (p_id) references Patient(p_id) on delete cascade
);

CREATE TABLE inpatient
(
    room_no int ,
    lab_no int,
    p_id int primary key,
    date_of_admit date,
    date_of_discharge date,
    foreign key (lab_no) references lab_report(lab_no) on delete cascade,
    foreign key (p_id) references Patient(p_id) on delete cascade
);

CREATE TABLE outpatient
(
    lab_no int,
    p_id int primary key,
    datee date,
    foreign key (p_id) references Patient(p_id) on delete cascade,
    foreign key (lab_no) references lab_report(lab_no) on delete cascade
);

CREATE TABLE rooms
(
    room_no int primary key,
    room_type varchar (10),
    status  varchar(20)
);

CREATE TABLE bills
(
    bill_no varchar(30) primary key,
    p_id int,
    no_of_days int,
    medicine_charges int,
    room_no int,
    foreign key (p_id) references Patient(p_id) on delete cascade,
    foreign key (room_no) references rooms (room_no) on delete cascade
);
