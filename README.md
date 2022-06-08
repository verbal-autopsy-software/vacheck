# vacheck

Data consistency checks for verbal autopsy (VA) data collected using the WHO 
VA instrument.

```python
from vacheck.datacheck5 import DataCheck5

# load probbase and look at relevant columns

# walk through examples at bottom
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
