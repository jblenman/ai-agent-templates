---
name: azure-devops-api
description: Azure DevOps REST API reference for work items, queries, pipelines, and repos
---
## Azure DevOps REST API Reference

The Azure DevOps CLI (`az devops`) does not work reliably in this environment. Use the REST API directly via PowerShell (`Invoke-RestMethod`) or curl.

## Authentication

Use a Personal Access Token (PAT) with Basic auth. The username is empty — only the PAT matters.

### PowerShell
```powershell
$pat = $env:AZURE_DEVOPS_PAT
$org = $env:AZURE_DEVOPS_ORG
$project = $env:AZURE_DEVOPS_PROJECT
$base = "https://dev.azure.com/$org/$project/_apis"

$headers = @{
    Authorization = "Basic " + [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes(":$pat"))
}
```

### curl
```bash
PAT="$AZURE_DEVOPS_PAT"
ORG="$AZURE_DEVOPS_ORG"
PROJECT="$AZURE_DEVOPS_PROJECT"
BASE="https://dev.azure.com/$ORG/$PROJECT/_apis"
AUTH=$(echo -n ":$PAT" | base64)
```

## Work Items

### Get a single work item
```powershell
Invoke-RestMethod -Uri "$base/wit/workitems/12345?`$expand=all&api-version=7.1" -Headers $headers
```

### Get multiple work items by ID
```powershell
$ids = "1,2,3,4,5"
Invoke-RestMethod -Uri "$base/wit/workitems?ids=$ids&`$expand=all&api-version=7.1" -Headers $headers
```

### Query work items (WIQL)

WIQL (Work Item Query Language) is SQL-like. POST a query to get matching work item IDs, then fetch details.

```powershell
# Step 1: Run WIQL query to get IDs
$query = @{
    query = "SELECT [System.Id], [System.Title], [System.State], [System.AssignedTo], [System.WorkItemType] FROM WorkItems WHERE [System.TeamProject] = @project AND [System.State] <> 'Closed' AND [System.State] <> 'Removed' ORDER BY [System.ChangedDate] DESC"
} | ConvertTo-Json

$result = Invoke-RestMethod -Uri "$base/wit/wiql?api-version=7.1" -Method POST -Headers $headers -ContentType "application/json" -Body $query

# Step 2: Fetch full details for returned IDs
$ids = ($result.workItems | Select-Object -First 50).id -join ","
if ($ids) {
    $items = Invoke-RestMethod -Uri "$base/wit/workitems?ids=$ids&`$expand=all&api-version=7.1" -Headers $headers
    $items.value | ForEach-Object {
        [PSCustomObject]@{
            ID       = $_.id
            Type     = $_.fields.'System.WorkItemType'
            Title    = $_.fields.'System.Title'
            State    = $_.fields.'System.State'
            Assigned = $_.fields.'System.AssignedTo'.displayName
            Priority = $_.fields.'Microsoft.VSTS.Common.Priority'
        }
    } | Format-Table -AutoSize
}
```

### Common WIQL Queries

**My active work items:**
```sql
SELECT [System.Id], [System.Title], [System.State], [System.WorkItemType]
FROM WorkItems
WHERE [System.TeamProject] = @project
  AND [System.AssignedTo] = @me
  AND [System.State] <> 'Closed'
  AND [System.State] <> 'Removed'
ORDER BY [Microsoft.VSTS.Common.Priority] ASC, [System.ChangedDate] DESC
```

**All active bugs:**
```sql
SELECT [System.Id], [System.Title], [System.State], [System.AssignedTo], [Microsoft.VSTS.Common.Priority]
FROM WorkItems
WHERE [System.TeamProject] = @project
  AND [System.WorkItemType] = 'Bug'
  AND [System.State] <> 'Closed'
  AND [System.State] <> 'Removed'
ORDER BY [Microsoft.VSTS.Common.Priority] ASC
```

**Tasks in current sprint:**
```sql
SELECT [System.Id], [System.Title], [System.State], [System.AssignedTo]
FROM WorkItems
WHERE [System.TeamProject] = @project
  AND [System.WorkItemType] = 'Task'
  AND [System.IterationPath] = @currentIteration('[your-team]')
ORDER BY [System.State] ASC
```

**Recently changed (last 7 days):**
```sql
SELECT [System.Id], [System.Title], [System.State], [System.ChangedDate]
FROM WorkItems
WHERE [System.TeamProject] = @project
  AND [System.ChangedDate] >= @today - 7
ORDER BY [System.ChangedDate] DESC
```

**Items by area path:**
```sql
SELECT [System.Id], [System.Title], [System.State]
FROM WorkItems
WHERE [System.TeamProject] = @project
  AND [System.AreaPath] UNDER 'ProjectName\AreaName'
  AND [System.State] <> 'Closed'
```

### Create a work item
```powershell
$body = @(
    @{ op = "add"; path = "/fields/System.Title"; value = "New task title" }
    @{ op = "add"; path = "/fields/System.Description"; value = "<p>Description here</p>" }
    @{ op = "add"; path = "/fields/System.AssignedTo"; value = "user@example.com" }
    @{ op = "add"; path = "/fields/Microsoft.VSTS.Common.Priority"; value = 2 }
) | ConvertTo-Json -AsArray

# Type goes in the URL: $Task, $Bug, $User Story, etc.
Invoke-RestMethod -Uri "$base/wit/workitems/`$Task?api-version=7.1" -Method POST -Headers $headers -ContentType "application/json-patch+json" -Body $body
```

### Update a work item
```powershell
$body = @(
    @{ op = "replace"; path = "/fields/System.State"; value = "Active" }
    @{ op = "add"; path = "/fields/System.History"; value = "Updated via REST API" }
) | ConvertTo-Json -AsArray

Invoke-RestMethod -Uri "$base/wit/workitems/12345?api-version=7.1" -Method PATCH -Headers $headers -ContentType "application/json-patch+json" -Body $body
```

### Add a comment to a work item
```powershell
$body = @{ text = "Comment text here" } | ConvertTo-Json
Invoke-RestMethod -Uri "$base/wit/workitems/12345/comments?api-version=7.1-preview.4" -Method POST -Headers $headers -ContentType "application/json" -Body $body
```

### Get work item history/updates
```powershell
Invoke-RestMethod -Uri "$base/wit/workitems/12345/updates?api-version=7.1" -Headers $headers
```

## Pipelines

### List pipelines
```powershell
Invoke-RestMethod -Uri "$base/pipelines?api-version=7.1" -Headers $headers
```

### Get recent pipeline runs
```powershell
$pipelineId = 42
Invoke-RestMethod -Uri "$base/pipelines/$pipelineId/runs?api-version=7.1" -Headers $headers
```

### Get a specific run
```powershell
Invoke-RestMethod -Uri "$base/pipelines/$pipelineId/runs/$runId?api-version=7.1" -Headers $headers
```

### Trigger a pipeline run
```powershell
$body = @{
    resources = @{
        repositories = @{
            self = @{ refName = "refs/heads/main" }
        }
    }
} | ConvertTo-Json -Depth 5

Invoke-RestMethod -Uri "$base/pipelines/$pipelineId/runs?api-version=7.1" -Method POST -Headers $headers -ContentType "application/json" -Body $body
```

## Git Repositories

### List repos
```powershell
Invoke-RestMethod -Uri "$base/git/repositories?api-version=7.1" -Headers $headers
```

### Get pull requests
```powershell
$repoId = "repo-name-or-guid"
Invoke-RestMethod -Uri "$base/git/repositories/$repoId/pullrequests?searchCriteria.status=active&api-version=7.1" -Headers $headers
```

### Get PR details with threads (comments)
```powershell
$prId = 100
Invoke-RestMethod -Uri "$base/git/repositories/$repoId/pullrequests/$prId/threads?api-version=7.1" -Headers $headers
```

## Build (Classic)

### List build definitions
```powershell
Invoke-RestMethod -Uri "$base/build/definitions?api-version=7.1" -Headers $headers
```

### Get recent builds
```powershell
Invoke-RestMethod -Uri "$base/build/builds?`$top=10&api-version=7.1" -Headers $headers
```

## Common Field Names

| Field | Path |
|-------|------|
| Title | `System.Title` |
| State | `System.State` |
| Assigned To | `System.AssignedTo` |
| Work Item Type | `System.WorkItemType` |
| Area Path | `System.AreaPath` |
| Iteration Path | `System.IterationPath` |
| Priority | `Microsoft.VSTS.Common.Priority` |
| Severity | `Microsoft.VSTS.Common.Severity` |
| Description | `System.Description` |
| Repro Steps | `Microsoft.VSTS.TCM.ReproSteps` |
| Acceptance Criteria | `Microsoft.VSTS.Common.AcceptanceCriteria` |
| Story Points | `Microsoft.VSTS.Scheduling.StoryPoints` |
| Remaining Work | `Microsoft.VSTS.Scheduling.RemainingWork` |
| Tags | `System.Tags` |
| Created Date | `System.CreatedDate` |
| Changed Date | `System.ChangedDate` |
| Created By | `System.CreatedBy` |
| Changed By | `System.ChangedBy` |
| History | `System.History` |
| Parent | `System.Parent` |

## Error Handling

Common errors:
- **401 Unauthorized** — PAT expired or missing scope. Generate a new PAT with "Work Items (Read/Write)" scope.
- **404 Not Found** — wrong org/project name, or work item doesn't exist.
- **400 Bad Request** — usually malformed WIQL or JSON Patch body. Check query syntax.
- **VS403429 Rate Limited** — too many requests. Back off and retry.

## Tips

- WIQL `@me` resolves to the PAT owner's identity
- WIQL `@project` resolves to the project in the URL
- WIQL `@today` is the current date
- `$expand=all` on work items returns relations (parent/child links)
- IDs returned by WIQL may include items you can't access — handle 404s gracefully
- Maximum 200 IDs per `workitems?ids=` request — batch if needed
- `ConvertTo-Json -Depth 5` prevents PowerShell from truncating nested objects
