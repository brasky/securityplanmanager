from django.db import models

class Control(models.Model):
	number = models.CharField(max_length=20, unique=True)
	control_text = models.TextField()
	supplemental_guidance = models.TextField()
	def __str__(self):
		return self.number	


class Team(models.Model):
	name = models.CharField(max_length=20, unique=True)

	def __str__(self):
		return self.name

class Implementation(models.Model):
	
	IMPLEMENTATION_STATUS_CHOICES = (
		('IM', 'Implemented'),
		('PI', 'Partially Implemented'),
		('PL', 'Planned'),
		('AI', 'Alternative Implementation'),
		('NA', 'Not Applicable'),
	)
	CONTROL_ORIGINATION_CHOICES = (
		('SPC', 'Service Provider Corporate'),
		('SPS', 'Service Provider System Specific'),
		('SPH', 'Service Provider Hybrid (Corporate and System Specific)'),
		('CBC', 'Configured by Customer (Customer System Specific)'),
		('PBC', 'Provided by Customer (Customer System Specific)'),
		('SHA', 'Shared (Service Provider and Customer Responsibility)'),
		('INH', 'Inherited from pre-existing Provisional Authority to Operate (P-ATO)'),
		('NOT', 'Not Applicable'),
	)	
	control = models.ForeignKey('Control', on_delete=models.CASCADE)
	parameter = models.TextField()
	customer_responsibility = models.TextField()	
	solution = models.TextField()
	implementation_status = models.CharField(
		max_length=2,
		choices=IMPLEMENTATION_STATUS_CHOICES,
		default="IM",
	)
	control_origination = models.CharField(
		max_length=3,
		choices=CONTROL_ORIGINATION_CHOICES,
		default='SPS',
	)
	def team_default():
		return Team.objects.all()	
	
	teams = models.ManyToManyField(Team,related_name='teams', default=team_default)	

	def status_verbose(self):
		return dict(Implementation.IMPLEMENTATION_STATUS_CHOICES)[self.implementation_status]

	def origination_verbose(self):
		return dict(Implementation.CONTROL_ORIGINATION_CHOICES)[self.control_origination]

	def __str__(self):
		team_object_list = list(self.teams.all())
		team_list = [team.name for team in team_object_list]
		name = self.control.number + " - " + ' '.join(team_list)
		return name 

