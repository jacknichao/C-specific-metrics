package com.alibaba.force.api.v3.tag;

import com.alibaba.force.base.shared.authentication.annotation.AuthType;
import com.alibaba.force.base.shared.model.enums.AuthTypeEnum;
import com.alibaba.force.base.tag.Tags;
import com.alibaba.force.base.tag.model.dto.ReleaseDTO;
import com.alibaba.force.base.tag.model.dto.TagCreateDTO;
import com.alibaba.force.base.tag.model.dto.TagDTO;
import com.alibaba.force.base.tag.model.dto.TagReleaseDTO;
import com.alibaba.force.base.tag.model.dto.TagsDTO;
import com.alibaba.force.common.exception.http.NoSuchTagException;
import com.alibaba.force.common.exception.http.ProjectNotFoundException;
import com.alibaba.force.common.exception.http.ReleaseAlreadyExistsException;
import com.alibaba.force.common.exception.http.ReleaseNotFoundException;
import com.alibaba.force.common.exception.http.RepositoryNotFoundException;
import com.alibaba.force.common.exception.http.TagAlreadyExistsException;
import com.alibaba.force.common.exception.http.TagNameInvalidException;
import com.alibaba.force.common.exception.http.TagNotExistsException;

import io.swagger.annotations.ApiOperation;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.RestController;

/**
 * @author dyroneteng
 * @date 2017/10/10
 */
@RestController
@RequestMapping(value = "/api/v3/projects/{projectId}/repository/tags")
public class TagsRest {
    /**
     * 获取project下的tags
     * pagination: no
     * order: tag name默认desc
     *
     * @return List
     */
    @AuthType(authType = AuthTypeEnum.PRIVATE_TOKEN)
    @ApiOperation(httpMethod = "GET", value = "List project tag.")
    @RequestMapping(method = RequestMethod.GET,
        produces = MediaType.APPLICATION_JSON_UTF8_VALUE)
    public ResponseEntity list(
        @PathVariable("projectId") Long projectId)
        throws RepositoryNotFoundException, ProjectNotFoundException {
        return new ResponseEntity(tags.list(projectId), HttpStatus.OK);
    }

    /**
     * create tag
     *
     * @return TagsDTO
     */
    @AuthType(authType = AuthTypeEnum.PRIVATE_TOKEN)
    @ApiOperation(httpMethod = "POST", value = "create project tag.")
    @RequestMapping(method = RequestMethod.POST,
        produces = MediaType.APPLICATION_JSON_UTF8_VALUE)
    public ResponseEntity<TagsDTO> create(
        @PathVariable("projectId") Long projectId,
        @Validated @RequestBody TagCreateDTO tagCreateDTO)
        throws RepositoryNotFoundException, ReleaseAlreadyExistsException, ProjectNotFoundException,
        TagAlreadyExistsException, TagNameInvalidException {
        tagCreateDTO.setTagName(tagCreateDTO.getTagName().trim());
        return new ResponseEntity<>(tags.add(projectId,
            tagCreateDTO.getTagName(), tagCreateDTO.getRef(), tagCreateDTO.getMessage(), tagCreateDTO.getDescription()),
            HttpStatus.CREATED);
    }

    /**
     * get a single tag
     *
     * @param projectId
     * @param tagName
     * @return
     * @throws RepositoryNotFoundException
     * @throws ProjectNotFoundException
     */
    @AuthType(authType = AuthTypeEnum.PRIVATE_TOKEN)
    @RequestMapping(value = "/{tagName}", method = RequestMethod.GET,
        produces = MediaType.APPLICATION_JSON_UTF8_VALUE)
    public ResponseEntity<TagsDTO> getSingleTag(
        @PathVariable Long projectId, @PathVariable String tagName)
        throws RepositoryNotFoundException, ProjectNotFoundException, TagNotExistsException {
        return new ResponseEntity<>(tags.get(projectId, tagName), HttpStatus.OK);
    }

    /**
     * delete tag
     * @param projectId
     * @param tagName
     * @return
     * @throws NoSuchTagException
     * @throws RepositoryNotFoundException
     * @throws ProjectNotFoundException
     */
    @AuthType(authType = AuthTypeEnum.PRIVATE_TOKEN)
    @ApiOperation(httpMethod = "DELETE", value = "delete project tag.")
    @RequestMapping(value = "/{tagName}",method = RequestMethod.DELETE,
        produces = MediaType.APPLICATION_JSON_UTF8_VALUE)
    public ResponseEntity<TagDTO> delete(
        @PathVariable("projectId") Long projectId,
        @PathVariable("tagName") String tagName
    ) throws NoSuchTagException, RepositoryNotFoundException, ProjectNotFoundException {
        return new ResponseEntity<>(tags.delete(projectId, tagName), HttpStatus.OK);
    }

    /**
     * create a new release
     *
     * @return TagReleaseDTO
     */
    @AuthType(authType = AuthTypeEnum.PRIVATE_TOKEN)
    @ApiOperation(httpMethod = "POST", value = "create a new release.")
    @RequestMapping(value = "/{tagName}/release", method = RequestMethod.POST)
    public ResponseEntity<TagReleaseDTO> createRelease(@PathVariable("projectId") Long projectId,
        @PathVariable("tagName") String tagName, @Validated @RequestBody ReleaseDTO releaseDTO)
        throws ReleaseAlreadyExistsException, ProjectNotFoundException, TagNotExistsException {
        return new ResponseEntity<>(tags.addRelease(projectId, tagName, releaseDTO.getDescription()),
            HttpStatus.CREATED);
    }

    /**
     * update a new release
     *
     * @return TagReleaseDTO
     */
    @AuthType(authType = AuthTypeEnum.PRIVATE_TOKEN)
    @ApiOperation(httpMethod = "PUT", value = "update a new release.")
    @RequestMapping(value = "/{tagName}/release", method = RequestMethod.PUT,
        produces = MediaType.APPLICATION_JSON_UTF8_VALUE)
    public ResponseEntity<TagReleaseDTO> updateRelease(@PathVariable("projectId") Long projectId,
                                                       @PathVariable("tagName") String tagName,
                                                       @Validated @RequestBody ReleaseDTO releaseDTO)
        throws ReleaseNotFoundException, ProjectNotFoundException, TagNotExistsException {
        String description = releaseDTO == null ? null : releaseDTO.getDescription();
        return new ResponseEntity<>(tags.updRelease(projectId, tagName, description), HttpStatus.OK);
    }

    @Autowired
    public TagsRest(Tags tags) {
        this.tags = tags;
    }

    private Tags tags;
}
