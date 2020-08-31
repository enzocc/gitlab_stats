import gitlab
from collections import defaultdict
import datetime
from matplotlib import pyplot as plt
import numpy as np
from collections import Counter


PROJECT_ID = 999  # Update with ProjectID
CONFIG_ID = 'config_id'  # Update with your CONFIG_ID

TEAM = {
    'user1': 'user1@example.org',
    'user2': 'user2@example.org',
    'user3': 'user3@example.org',
    'user4': 'user4@example.org',
}

COLORS = {
    'user1': '#d45087',
    'user2': '#665191',
}

REGTECH = {
    'user1', 'user2'
}

BACKEND = {
    'user3'
}

FRONTEND = {
    'user4'
}

INTERVALS = {
    'Jun-2019': ('2019-06-01', '2019-07-01'),
    'Jul-2019': ('2019-07-01', '2019-08-01'),
    'Aug-2019': ('2019-08-01', '2019-09-01'),
    'Sep-2019': ('2019-09-01', '2019-10-01'),
    'Oct-2019': ('2019-10-01', '2019-11-01'),
    'Nov-2019': ('2019-11-01', '2019-12-01'),
    'Dec-2019': ('2019-12-01', '2020-01-01'),
    'Jan-2020': ('2020-01-01', '2020-02-01'),
    'Feb-2020': ('2020-02-01', '2020-03-01'),
    'Mar-2020': ('2020-03-01', '2020-04-01'),
    'Apr-2020': ('2020-04-01', '2020-05-01'),
    'May-2020': ('2020-05-01', '2020-06-01'),
    'Jun-2020': ('2020-06-01', '2020-07-01'),
    'Jul-2020': ('2020-07-01', '2020-08-01'),
    'Aug-2020': ('2020-08-01', '2020-09-01'),
}

TIME_OF_DAY = (
    [
        datetime.datetime.strptime('09:00:00', "%H:%M:%S").time(),
        datetime.datetime.strptime('18:30:00', "%H:%M:%S").time()
    ],
)


def divide_by_timeofday(commits, no_weekends=True):
    """
    - no_weekends:
    Returns: [n1, n2, ...]
    """
    c_split = [0]*len(TIME_OF_DAY)

    for c in commits:
        created_at = c.attributes['created_at']
        created_at = datetime.datetime.strptime(
            created_at.split('.')[0], "%Y-%m-%dT%H:%M:%S"
        )
        # Check if commit was created on the weekend
        if no_weekends and created_at.weekday() in [5, 6]:
            continue

        created_at = created_at.time()
        for index, [start, end] in enumerate(TIME_OF_DAY):
            if start < created_at <= end:
                c_split[index] += 1
                break
    return c_split


def get_average(values, key, sub_team):
    res = []
    for i in range(len(INTERVALS)):
        temp = [
            values[person][key][i] for person in sub_team
            if values[person][key] != 0
        ]
        res.append(sum(temp)/len(temp))

    return res


def get_avg_rate(values, partial_label, total_label, sub_team):
    res = []
    for i in range(len(INTERVALS)):
        partial_in_interval = [
            values[person][partial_label][i] for person in sub_team
        ]
        total_in_interval = [
            values[person][total_label][i] for person in sub_team
        ]
        res.append(sum(partial_in_interval)/(sum(total_in_interval)+0.0))

    return res


def plot_results(values_to_plot):
    x_axis = list(INTERVALS.keys())
    width = 0.08

    # Create indexes per user
    x_indexes = {}
    for index, member in enumerate(REGTECH):
        x_indexes[member] = np.arange(len(x_axis)) + index*width

    # I. Pipelines
    # Create sub-plots
    fig1, (ax1, ax2) = plt.subplots(2)
    fig1.suptitle("Pipeline Analysis")

    # Plot pipelines per month
    for k, v in values_to_plot.items():
        if k not in REGTECH:
            continue
        ax1.bar(x_indexes[k], v['total_pipelines'],
                width=width-0.02, color=COLORS[k], label=k)
        ax1.bar(x_indexes[k], v['succeeded_pipelines'],
                width=width-0.02, color="0.5", label=None)

    # Plot pipelines averages
    regtech_average = get_average(values_to_plot, "total_pipelines", REGTECH)
    backend_average = get_average(values_to_plot, "total_pipelines", BACKEND)
    frontend_average = get_average(values_to_plot, "total_pipelines", FRONTEND)
    ax1.plot(x_axis, regtech_average, color="#000000",
             linestyle='--', label="RegTech average")
    ax1.plot(x_axis, backend_average, color='#ffa100',
             linestyle='--', label="Backend average")
    ax1.plot(x_axis, frontend_average, color='#794e14',
             linestyle='--', label="Frontend average")

    # Plot pipeline success rate
    regtech_average = get_avg_rate(
        values_to_plot, "succeeded_pipelines", "total_pipelines", REGTECH)
    backend_average = get_avg_rate(
        values_to_plot, "succeeded_pipelines", "total_pipelines", BACKEND)
    frontend_average = get_avg_rate(
        values_to_plot, "succeeded_pipelines", "total_pipelines", FRONTEND)
    ax2.plot(x_axis, regtech_average, color="#000000",
             linestyle='--', label="RegTech pipeline success rate")
    ax2.plot(x_axis, backend_average, color='#ffa100',
             linestyle='--', label="Backend pipeline success rate")
    ax2.plot(x_axis, frontend_average, color='#794e14',
             linestyle='--', label="Frontend pipeline success rate")

    # Set legends and labels
    ax1.legend()
    ax1.set(ylabel="Number of pipelines")
    ax1.grid(True)
    ax2.set(ylabel="Average Success rate")
    ax2.grid(True)
    plt.show()

    # II. Commits
    # Create sub-plots
    fig2, (ax1, ax2) = plt.subplots(2)
    fig2.suptitle("Commit Analysis")

    # Plot commits
    for k, v in values_to_plot.items():
        if k not in REGTECH:
            continue
        ax1.bar(x_indexes[k], v['total_commits'],
                width=width-0.02, color=COLORS[k], label=k)
        ax1.bar(x_indexes[k], v['t0'],
                width=width-0.02, color="0.5", label=None)

    # Plot commit averages
    regtech_average = get_average(values_to_plot, "total_commits", REGTECH)
    backend_average = get_average(values_to_plot, "total_commits", BACKEND)
    frontend_average = get_average(values_to_plot, "total_commits", FRONTEND)

    ax1.plot(x_axis, regtech_average, color="#000000",
             linestyle='--', label="RegTech average")
    ax1.plot(x_axis, backend_average, color='#ffa100',
             linestyle='--', label="Backend average")
    ax1.plot(x_axis, frontend_average, color='#794e14',
             linestyle='--', label="Frontend average")

    # Plot Working hours portion
    regtech_average = get_avg_rate(
        values_to_plot, "t0", "total_commits", REGTECH)
    backend_average = get_avg_rate(
        values_to_plot, "t0", "total_commits", BACKEND)
    frontend_average = get_avg_rate(
        values_to_plot, "t0", "total_commits", FRONTEND)
    ax2.plot(x_axis, regtech_average, color="#000000",
             linestyle='--', label="RegTech - Working hours rate")
    ax2.plot(x_axis, backend_average, color='#ffa100',
             linestyle='--', label="Backend - Working hours rate")
    ax2.plot(x_axis, frontend_average, color='#794e14',
             linestyle='--', label="Frontend - Working hours rate")

    # Set legends and labels
    # plt.setxticks(ticks=np.arange(len(x_axis)), labels=x_axis)
    ax1.legend()
    ax1.set(ylabel="Number of Commits")
    ax1.grid(True)
    ax2.set(ylabel="Average Rate of Commits in Working Hours")
    ax2.grid(True)
    plt.show()


def pipelines_per_user(intervals, team_members, results):
    """
    Returns:
    {
        enzo:{
            total_pipelines: [n1, n2, ... ]
            succeeded_pipelines: [n3, n4, ... ]
        },
        jonathan: { ... },
        ...
    }
    """
    for team_member in team_members:
        results[team_member] = defaultdict(list)
        for i in intervals:
            pipelines = services.pipelines.list(
                updated_after=i[0],
                updated_before=i[1],
                username=team_member,
                all=True
            )
            total = len(pipelines)
            success = len(
                [p for p in pipelines if p.attributes['status'] == 'success']
            )

            results[team_member]['total_pipelines'].append(total)
            results[team_member]['succeeded_pipelines'].append(success)

    return results


def commits_per_user(intervals, team_members, results):
    """
    Returns:
    {
        enzo:{
            total_commits: [n1, n2, ... ]
            t1:[n5, n6, ... ]
            t2:[n7, n8, ... ]
            t3:[n9, n9, ... ]
            t4:[n11, n10, ... ]
            ...
        },
        jonathan: { ... },
        ...
    }
    """
    for i in intervals:
        # Commit for interval i
        commits = services.commits.list(
            ref_name='master',
            since=i[0],
            until=i[1],
            all=True
        )
        # Commit per user in interval i
        commits_per_user = {}
        for member, email in team_members.items():
            commits_per_user[member] = [
                c for c in commits if c.attributes['author_email'] == email
            ]

        for member, commits in commits_per_user.items():
            results[member]['total_commits'].append(len(commits))
            split_commits = divide_by_timeofday(commits)

            for index, number_of_commits in enumerate(split_commits):
                results[member]['t{}'.format(index)].append(number_of_commits)

    return results


def time_master_pipeline(project, interval):
    """
    Measures the time taken for the successful master pipelines to
    """
    result = []
    for i in interval:
        pipelines = project.pipelines.list(
            status='success',
            ref='master',
            updated_after=i[0],
            updated_before=i[1],
            all=True
        )
        # Get the pipelines length in the interval
        lengths = []
        for pip in pipelines:
            start = datetime.datetime.strptime(
                pip.created_at, "%Y-%m-%dT%H:%M:%S.%fZ")
            end = datetime.datetime.strptime(
                pip.updated_at, "%Y-%m-%dT%H:%M:%S.%fZ")
            duration = (end-start).days*3600*24 + (end-start).seconds
            lengths.append(duration/60.0)
        # Attach statistics to the result arrays
        result.append(lengths)
    return result


def time_other_pipeline(project, interval):
    """
    Measures the time taken for the successful pipelines
    """
    result = []
    failed = []

    for i in interval:
        # Get all pipelines
        pipelines = project.pipelines.list(
            status='success',
            updated_after=i[0],
            updated_before=i[1],
            all=True
        )
        # Filter out master pipelines
        pipelines = [p for p in pipelines if p.ref not in [
            'master', 'RegTech']]
        if i in list(interval)[-3:]:
            failed_jobs = Counter(
                [j.name for p in pipelines for j in p.jobs.list(
                    scope='failed')]
            )
            # Remove fixme job (set to failed anyway)
            try:
                failed_jobs.pop('fixme')
            except KeyError:
                pass
            failed.append([len(pipelines), i, failed_jobs])

        lengths = []
        for pip in pipelines:
            start = datetime.datetime.strptime(
                pip.created_at, "%Y-%m-%dT%H:%M:%S.%fZ")
            end = datetime.datetime.strptime(
                pip.updated_at, "%Y-%m-%dT%H:%M:%S.%fZ")
            duration = (end-start).days*3600*24 + (end-start).seconds

            # Check pipelines taking less than 55 min
            if duration < 55*60:
                # Case 1: Less than 60 jobs aren't standard:
                if len(pip.jobs.list(all=True)) < 60:
                    continue
                # Case 2: Associated to a MR not targetting master
                if "merge-requests" in pip.ref:
                    mr = int(pip.ref.split('/')[2])
                    if project.mergerequests.get(mr).target_branch != 'master':
                        continue
            lengths.append(duration/60.0)
        # Attach statistics to the result arrays
        result.append(lengths)
    return result, failed


def fail_other_pipeline(project, interval):
    """
    Measures the time taken for failed pipelines
    """
    result = []

    for i in interval:
        # Get all pipelines
        pipelines = project.pipelines.list(
            status='failed',
            updated_after=i[0],
            updated_before=i[1],
            all=True
        )
        # Filter out master pipelines
        pipelines = [p for p in pipelines if p.ref not in [
            'master', 'RegTech']]

        lengths = []
        for pip in pipelines:
            start = datetime.datetime.strptime(
                pip.created_at, "%Y-%m-%dT%H:%M:%S.%fZ")
            end = datetime.datetime.strptime(
                pip.updated_at, "%Y-%m-%dT%H:%M:%S.%fZ")
            duration = (end-start).days*3600*24 + (end-start).seconds

            lengths.append(duration/60.0)
        # Attach statistics to the result arrays
        result.append(lengths)
    return result


def plot_pipelines_box_stats(array, title):
    """
    Plot the box stats for the pipelines
    """
    fig1, ax1 = plt.subplots()
    fig1.suptitle(title)
    ax1.boxplot(array, showfliers=False, meanline=True)
    ax1.grid(which='major', alpha=0.7)
    ax1.grid(which='minor', alpha=0.3)
    plt.xticks(list(range(1, len(INTERVALS)+1)), list(INTERVALS.keys()))
    plt.minorticks_on()
    plt.show()


def plot_pipeline_wcs(array, title):
    """
    Plot the Worst Case Scenarios for the pipelines
    """
    x_axis = list(INTERVALS.keys())
    fig1, ax1 = plt.subplots()
    array_wcs = [max(t) for t in array]
    fig1.suptitle(title)
    ax1.plot(x_axis, array_wcs)
    ax1.grid(which='major', alpha=0.7)
    ax1.grid(which='minor', alpha=0.3)
    plt.minorticks_on()
    plt.show()


def plot_common_errors(error_names, error_counts, interval, total_pipelines):
    """
    Plot the most common errors in successful pipelines
    """
    plt.rcdefaults()
    fig, ax = plt.subplots()
    fig.suptitle("Jobs failed in {}. Total pipelines: {}".format(
        interval, total_pipelines))
    y_pos = np.arange(len(error_names))
    ax.barh(y_pos, error_counts)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(error_names)
    ax.grid(True)
    plt.show()


gl = gitlab.Gitlab.from_config(CONFIG_ID)
services = gl.projects.get(PROJECT_ID)

results = {}
for team_member in TEAM:
    results[team_member] = defaultdict(list)

t_master = time_master_pipeline(services, INTERVALS.values())
t_others, t_jobs_failed = time_other_pipeline(services, INTERVALS.values())
t_failed = fail_other_pipeline(services, INTERVALS.values())

pipelines_per_user(INTERVALS.values(), TEAM, results)
commits_per_user(INTERVALS.values(), TEAM, results)
plot_results(results)

plot_pipelines_box_stats(t_master, 'Time of Master pipeline (in min)')
plot_pipeline_wcs(t_master, 'WCS of Master pipeline (in min)')

plot_pipelines_box_stats(t_others, 'Time of Non-Master pipelines (in min)')
plot_pipeline_wcs(t_others, 'WCS of Non-Master pipelines (in min)')

plot_pipelines_box_stats(t_failed, 'Time to failure (in min)')
plot_pipeline_wcs(t_failed, 'WCS to failure (in min)')


for i in range(len(t_jobs_failed)):
    plot_common_errors(t_jobs_failed[i][2].keys(
    ), t_jobs_failed[i][2].values(), t_jobs_failed[i][1], t_jobs_failed[i][0])
