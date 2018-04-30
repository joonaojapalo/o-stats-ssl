select
	c.name, re.placing, re.time, re.diff_time, ru.name, ru.club
from
	results as re
join
	runners as ru on ru.id = re.runner_id
join
	competitions as c on c.id = re.competition_id
where
	club = 'Lynx'
order by
	re.competition_id, re.class, re.placing asc;
