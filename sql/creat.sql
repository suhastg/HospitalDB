create table patient
(
    patient_id int auto_increment primary key,
    name varchar(20) not null,
    dob date not null,
    gender varchar(10) not null,
    email varchar(30) not null unique
);

create table doctor
(
    doctor_id int auto_increment primary key,
    name varchar(20) not null,
    dept varchar(20) not null,
    email varchar(30) not null unique,
    dob date not null,
    fees FLOAT NOT NULL default 1000.00
);

create table consultation
(
    consult_id int auto_increment unique,
    patient_id int not null,
    doctor_id int not null,
    consult_date datetime not null,
    fees float not null,

    primary key (patient_id, doctor_id, consult_date),

    foreign key(patient_id) references patient(patient_id) on delete cascade,
    foreign key(doctor_id)  references doctor(doctor_id) on delete cascade

);

create table lab_report
(
    report_id int auto_increment primary key,
    consult_id int not null,
    report_type varchar(20) not null,
    fee float not null,
    foreign key(consult_id) references consultation(consult_id) on delete cascade
);

create table patient_report
(
    consult_id int not null,
    doctor_msg text not null,
    medicine varchar(20) not null,
     primary key (consult_id),
    foreign key(consult_id) references consultation(consult_id) on delete cascade
);