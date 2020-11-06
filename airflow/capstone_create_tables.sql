CREATE TABLE public.staging_covid_cases (
    "date" date, 
    country varchar(128),
    confirmed int4,
    recovered int4,
    deaths int4 
);

CREATE TABLE public.covid_cases (
    "date" date, 
    country varchar(128),
    confirmed int4,
    recovered int4,
    deaths int4,
    CONSTRAINT covid_cases_pkey PRIMARY KEY ("date", country)
);

CREATE TABLE public.countries(
    name varchar(128),
    countrycode char(2),
    CONSTRAINT countries_pkey PRIMARY KEY (name)
);

CREATE TABLE public.staging_tweets(
    tweetid bigint NOT NULL,
    "date" date, 
    "time" timetz,
    lang varchar(3),
    countrycode char(2) 
);

CREATE TABLE public.covid_reactions(
    number_of_tweets int, 
    "date" date,
    country varchar(128),
    confirmed int4,
    recovered int4,
    deaths int4,
    CONSTRAINT covid_reactions_pkey PRIMARY KEY ("date",country)
);