# vacheck

[![pytest](https://github.com/verbal-autopsy-software/vacheck/workflows/python-package/badge.svg)]

Data consistency checks for verbal autopsy (VA) data collected using the WHO 
VA instrument.

```python
>>> from vacheck.datacheck5 import datacheck5, get_example_input
>>> input = get_example_input()
>>> input.head
<bound method NDFrame.head of        ID  i004a  i004b  i019a  i019b  i022a  i022b  i022c  i022d  i022e  ...  i450o  i451o  i452o  i453o  i454o  i455o  i456o  i457o  i458o  i459o
0      d1    NaN    NaN    1.0    NaN    1.0    NaN    NaN      0      0  ...      0      0      0      0      0      0      0      0      0      0
1      d2    NaN    NaN    NaN    1.0    1.0    NaN    NaN      0      0  ...      0      0      0      0      0      0      0      0      0      0
2      d3    NaN    NaN    1.0    NaN    NaN    1.0    NaN      0      0  ...      0      0      0      0      0      0      0      0      0      0
3      d4    NaN    NaN    NaN    1.0    NaN    NaN    1.0      0      0  ...      0      0      0      0      0      0      0      0      0      0
4      d5    NaN    NaN    1.0    NaN    NaN    NaN    1.0      0      0  ...      0      0      0      0      0      0      0      0      0      0
..    ...    ...    ...    ...    ...    ...    ...    ...    ...    ...  ...    ...    ...    ...    ...    ...    ...    ...    ...    ...    ...
195  d196    NaN    NaN    NaN    1.0    NaN    NaN    1.0      0      0  ...      0      0      0      0      0      0      0      0      0      0
196  d197    NaN    NaN    1.0    NaN    1.0    NaN    NaN      0      0  ...      0      0      0      0      0      0      0      0      0      0
197  d198    NaN    NaN    1.0    NaN    1.0    NaN    NaN      0      0  ...      0      0      0      0      0      0      0      0      0      0
198  d199    NaN    NaN    NaN    1.0    1.0    NaN    NaN      0      0  ...      0      0      0      0      0      0      0      0      0      0
199  d200    NaN    NaN    NaN    1.0    1.0    NaN    NaN      0      0  ...      0      0      0      0      0      0      0      0      0      0

[200 rows x 354 columns]>
>>> checked_input = datacheck5(va_input=input.iloc[0], va_id=input.at[0, "ID"])
>>> checked_input.get("output")
ID        d1
i004a    NaN
i004b    NaN
i019a    1.0
i019b    NaN
        ... 
i455o      0
i456o      0
i457o      0
i458o      0
i459o      0
Name: 0, Length: 354, dtype: object
>>> checked_input.get("first_pass")[0]
'd1   W610104-o (ever cry) only required for neonates - cleared in working information'
>>> checked_input.get("second_pass")
[]
>>> # run checks on entire DataFrame (takes a minute or two)
>>> check_all = input.apply(lambda x: datacheck5(x, x.ID)["output"], axis=1)
>>> check_all
       ID  i004a  i004b  i019a  i019b  i022a  i022b  i022c  i022d  i022e  ...  i450o  i451o  i452o  i453o  i454o  i455o  i456o  i457o  i458o  i459o
0      d1    NaN    NaN    1.0    NaN    1.0    NaN    NaN      0      0  ...      0      0      0      0      0      0      0      0      0      0
1      d2    NaN    NaN    NaN    1.0    1.0    NaN    NaN      0      0  ...      0      0      0      0      0      0      0      0      0      0
2      d3    NaN    NaN    1.0    NaN    NaN    1.0    NaN      0      0  ...      0      0      0      0      0      0      0      0      0      0
3      d4    NaN    NaN    NaN    1.0    NaN    NaN    1.0      0      0  ...      0      0      0      0      0      0      0      0      0      0
4      d5    NaN    NaN    1.0    NaN    NaN    NaN    1.0      0      0  ...      0      0      0      0      0      0      0      0      0      0
..    ...    ...    ...    ...    ...    ...    ...    ...    ...    ...  ...    ...    ...    ...    ...    ...    ...    ...    ...    ...    ...
195  d196    NaN    NaN    NaN    1.0    NaN    NaN    1.0      0      0  ...      0      0      0      0      0      0      0      0      0      0
196  d197    NaN    NaN    1.0    NaN    1.0    NaN    NaN      0      0  ...      0      0      0      0      0      0      0      0      0      0
197  d198    NaN    NaN    1.0    NaN    1.0    NaN    NaN      0      0  ...      0      0      0      0      0      0      0      0      0      0
198  d199    NaN    NaN    NaN    1.0    1.0    NaN    NaN      0      0  ...      0      0      0      0      0      0      0      0      0      0
199  d200    NaN    NaN    NaN    1.0    1.0    NaN    NaN      0      0  ...      0      0      0      0      0      0      0      0      0      0

[200 rows x 354 columns]
```

# Details

With the development of the [**InterVA** algorithm](http://www.byass.uk/interva/), 
several data consistency checks were designed to ensure that indicators and 
symptoms do not indicate conflicting information (e.g., male and pregnant).  
For example, the following are inconsistent:

* *ageInDays*: 10 days
* *How long did (s)he have a cough*: 4 weeks

The data checks try to reconcile inconsistencies like these.  In the original 
software the data checks were defined in **probbase.xls** 
(the symptom-cause-information matrix with the conditional probabilities of 
each symptom given a cause -- see below for more information on the SCI,
and the [InterVA User's Guide](http://www.byass.uk/interva/)).  

Each type of consistency check is performed for each VA record, and then the 
process is repeated a second time.

Before the consistency checks are run, any VA record with missing information
on age or sex are removed -- these indicators are necessary for running the
InterVA and InSilicoVA algorithms.

## How each data check is performed

There are 3 types of data consistency checks

1. **Don't ask**
    * **Necessary Conditions** (for inconsistency)
        + both symptoms have non-missing values
        + index symptom == (Y or N) value in `subst` probbase column 
        + symptom in the `dontaskX` probbase column == last character
        (Y or N) in that cell <br> (`dontaskX` ranges from `dontask1` to
        `dontask8`)
    * **Action**: index symptom is set to missing
    * the log message is "(don't ask symptom) cleared in working information"
   
2. **Ask if**
    * **Necessary Conditions**
      + the index symptom == (Y or N) value in the `subst` probbase
      column (and thus not a missing value)
      + the symptom listed in the `doaskif` probbase column *does not* equal 
      the last character in that cell
    * **Action**: assign the symptom listed in the `doaskif` to the last
    character (Y or N) in that cell (concatenated to the symptom label, 
    e.g., `i022cY`)
    * the log message is "(ask if symptom label) updated in working information"

3. **Neonates only**
   * **Necessary Conditions**
     + index symptom == (Y or N) value in the `subst` probbase column
       (and thus index symptom does not have a missing value)
     + the decedent was NOT a neonate
   * **Action**: assign the index symptom to missing
   * the log message is "(index symptom) only required for neonates - cleared
   in working information"

## probbase

Relevant columns in **probbase.xls**

* **indic** (column A)
* **subst** (column F)
* **dontask1 - dontask8** (columns H - O)
* **doaskif** (column P)
* **nnonly** (column Q)

```python
>>> from vacheck.datacheck5 import get_probbase
>>> probbase = get_probbase()
>>> probbase.iat[0, 2]
'probbase v18 20200403 '
>>> probbase.columns
Index(['indic', 'qdesc', 'sdesc', 'who_2016', 'ilab', 'subst', 'samb',
       'dontask1', 'dontask2', 'dontask3', 'dontask4', 'dontask5', 'dontask6',
       'dontask7', 'dontask8', 'doaskif', 'nnonly', 'a_nrp', 'a_pend_6w',
       'a_preg', 'b_0101', 'b_0102', 'b_0103', 'b_0104', 'b_0105', 'b_0106',
       'b_0107', 'b_0108', 'b_0109', 'b_0110', 'b_0111', 'b_0112', 'b_0199',
       'b_0201', 'b_0202', 'b_0203', 'b_0204', 'b_0205', 'b_0299', 'b_0301',
       'b_0302', 'b_0303', 'b_0401', 'b_0402', 'b_0403', 'b_0499', 'b_0501',
       'b_0502', 'b_0601', 'b_0602', 'b_0701', 'b_0801', 'b_0901', 'b_0902',
       'b_0903', 'b_0904', 'b_0905', 'b_0906', 'b_0907', 'b_0908', 'b_0999',
       'b_1001', 'b_1002', 'b_1003', 'b_1004', 'b_1006', 'b_1099', 'b_1101',
       'b_1102', 'b_1201', 'b_1202', 'b_1203', 'b_1204', 'b_1205', 'b_1206',
       'b_1207', 'b_1208', 'b_1209', 'b_1210', 'b_1299', 'b_9800', 'c_cult',
       'c_emer', 'c_hsys', 'c_inev', 'c_know', 'c_resr'],
      dtype='object')
>>> probbase[["indic", "subst", "dontask1", "dontask8", "doaskif", "nnonly"]]
     indic subst dontask1 dontask8 doaskif nnonly
1    prior   NaN      NaN      NaN     NaN    NaN
2    i004a     Y   i004bY      NaN     NaN    NaN
3    i004b     Y   i004aY      NaN     NaN    NaN
4    i019a     Y   i019bY      NaN     NaN    NaN
5    i019b     Y   i019aY      NaN     NaN    NaN
..     ...   ...      ...      ...     ...    ...
350  i455o     Y      NaN      NaN     NaN    NaN
351  i456o     Y      NaN      NaN     NaN    NaN
352  i457o     Y      NaN      NaN     NaN    NaN
353  i458o     N      NaN      NaN     NaN    NaN
354  i459o     Y      NaN      NaN     NaN    NaN

[354 rows x 6 columns]
```


## Examples

* *Don't ask*
  + Log message: "4 W610059-o (married) value inconsistent with W610022-a (65+) - 
  cleared in working information"
  + VA record ID is 4
  + `i059o` - Was she married at the time of death? (with `subst == Y`)
  + `i022a` - Was s(he) aged 65 years or more at death?
  + `dontask6` - `i022aY` (don't ask item for index symptom `i059o` if
  `i022a == Y`)
  + **action**: `i059a` is changed (in the working copy of the data) from
  Y to missing

* Ask If
  + Log message: "7 W610152-o (fev nsw) not flagged in category W610147-o 
  (fever) - updated in working information"
  + VA record ID is 7
  + `i152o` - Did (s)he have night sweats? (with `subst == Y`)
  + `i147o` - During the illness that led to death, did (s)he have a fever?
  + `doaskif` - do ask `i152o` if `i147o == Y`
  + **action** `i147o` is changed from missing to Y

* Neonates only
  + Log message: "103075 W610394-a (born 1st pr) only required for neonates -
  cleared in working information"
  + VA record ID is 103075
  + `i394a` - Was this baby born from the mother's first pregnancy?
  + VA record was not a neonatal death
  + **action** `i394a` is set to missing
